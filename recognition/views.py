import os
import logging
from pathlib import Path
from django.conf import settings
from django.core.files import File
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny

from .models import Detection, DetectedSign, RecognitionHistory
from .serializers import (
    DetectionSerializer, 
    DetectionDetailSerializer,
    RecognitionHistorySerializer
)
from traffic_signs.models import TrafficSign
from ai_engine.yolo_infer import predict_image_with_save, predict_video_with_save

logger = logging.getLogger(__name__)


class DetectionUploadRunView(generics.CreateAPIView):
    """
    API endpoint để upload hình ảnh/video và chạy nhận diện biển báo
    
    POST /api/recognition/upload-run/
    Form-data:
        - file: file upload (image hoặc video)
        - file_type: "image" hoặc "video"
    
    Response:
        {
            "success": true,
            "message": "Nhận diện thành công",
            "detection_id": 123,
            "file_type": "video",
            "detected_signs": [
                {
                    "id": 1,
                    "class_name": "Cấm rẽ trái",
                    "confidence": 0.95,
                    "start_time": 1.5,
                    "end_time": 3.2,
                    "traffic_sign": {
                        "sign_Code": "P.123",
                        "name": "Cấm rẽ trái",
                        "description": "...",
                        "category": "Biển cấm",
                        "penalty_details": "..."
                    }
                }
            ],
            "output_file_url": "http://localhost:8000/media/results/vid_xxx.mp4"
        }
    """
    serializer_class = DetectionSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]  # Hoặc IsAuthenticated nếu cần đăng nhập
    
    def create(self, request, *args, **kwargs):
        # Validate input
        file = request.FILES.get('file')
        file_type = request.data.get('file_type', '').lower()
        
        # Debug logging
        logger.info(f"Upload request - file: {file.name if file else 'None'}, file_type: '{file_type}'")
        logger.info(f"Request FILES: {request.FILES}")
        logger.info(f"Request data: {request.data}")
        
        if not file:
            return Response(
                {"success": False, "message": "Vui lòng upload file"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if file_type not in ['image', 'video']:
            return Response(
                {"success": False, "message": f"file_type phải là 'image' hoặc 'video'. Nhận được: '{file_type}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Kiểm tra định dạng file
        allowed_image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        allowed_video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        file_ext = os.path.splitext(file.name)[1].lower()
        
        if file_type == 'image' and file_ext not in allowed_image_extensions:
            return Response(
                {"success": False, "message": f"Định dạng ảnh không hợp lệ. Chỉ chấp nhận: {', '.join(allowed_image_extensions)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if file_type == 'video' and file_ext not in allowed_video_extensions:
            return Response(
                {"success": False, "message": f"Định dạng video không hợp lệ. Chỉ chấp nhận: {', '.join(allowed_video_extensions)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Tạo Detection object
        detection = Detection.objects.create(
            file=file,
            file_type=file_type,
            status='processing',
            user=request.user if request.user.is_authenticated else None
        )
        
        try:
            # Lấy đường dẫn file đã upload
            file_path = Path(detection.file.path)
            
            if file_type == 'image':
                # Xử lý ảnh
                detections, output_path = predict_image_with_save(file_path, conf=0.25)
                
                # Lưu output file
                with open(output_path, 'rb') as f:
                    detection.output_file.save(output_path.name, File(f), save=False)
                
                # Tạo DetectedSign cho ảnh
                self._create_detected_signs_for_image(detection, detections)
                
            else:  # video
                # Xử lý video
                frame_detections, output_path, fps = predict_video_with_save(file_path, conf=0.25)
                
                # Lưu output file
                with open(output_path, 'rb') as f:
                    detection.output_file.save(output_path.name, File(f), save=False)
                
                # Lưu thông tin video
                detection.fps = fps
                detection.total_frames = len(frame_detections)
                detection.duration = detection.total_frames / fps if fps > 0 else 0
                
                # Tạo DetectedSign cho video với timeline
                self._create_detected_signs_for_video(detection, frame_detections, fps)
            
            # Cập nhật status
            detection.status = 'done'
            detection.save()
            
            # Trả về response
            serializer = DetectionDetailSerializer(detection, context={'request': request})
            return Response({
                "success": True,
                "message": "Nhận diện thành công",
                "detection_id": detection.id,
                "file_type": file_type,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error processing detection {detection.id}: {str(e)}", exc_info=True)
            detection.status = 'failed'
            detection.error_message = str(e)
            detection.save()
            
            return Response({
                "success": False,
                "message": f"Lỗi khi xử lý: {str(e)}",
                "detection_id": detection.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _create_detected_signs_for_image(self, detection, detections):
        """Tạo DetectedSign cho ảnh"""
        for det in detections:
            class_id = det.get('class_id')
            class_name = det.get('class_name', '')
            
            # Tìm TrafficSign tương ứng
            traffic_sign = self._find_traffic_sign(class_id, class_name)
            
            DetectedSign.objects.create(
                detection=detection,
                traffic_sign=traffic_sign,
                class_id=class_id,
                class_name=class_name,
                confidence=det.get('confidence', 0),
                bbox=det.get('bbox', []),
                frame_index=0  # Ảnh chỉ có 1 frame
            )
    
    def _create_detected_signs_for_video(self, detection, frame_detections, fps):
        """
        Tạo DetectedSign cho video với timeline
        Gộp các detection của cùng một biển báo, cho phép gap nhỏ giữa các detections
        """
        GAP_TOLERANCE_FRAMES = int(fps * 0.5)  # Cho phép gap 0.5 giây giữa các detections
        MIN_APPEARANCE_DURATION = 0.3  # Chỉ giữ biển báo xuất hiện ít nhất 0.3 giây
        
        # Tập hợp tất cả detections theo biển báo
        # Key: (class_id, class_name), Value: list of {frame, confidence, bbox}
        all_detections_by_sign = {}
        
        for frame_data in frame_detections:
            frame_idx = frame_data['frame_index']
            detections = frame_data['detections']
            
            for det in detections:
                class_id = det.get('class_id')
                class_name = det.get('class_name', '')
                key = (class_id, class_name)
                
                if key not in all_detections_by_sign:
                    all_detections_by_sign[key] = []
                
                all_detections_by_sign[key].append({
                    'frame': frame_idx,
                    'confidence': det.get('confidence', 0),
                    'bbox': det.get('bbox', [])
                })
        
        # Xử lý từng biển báo
        for (class_id, class_name), detections_list in all_detections_by_sign.items():
            # Sắp xếp theo frame
            detections_list.sort(key=lambda x: x['frame'])
            
            # Gộp các detections gần nhau thành các segments
            segments = []
            current_segment = None
            
            for det in detections_list:
                frame = det['frame']
                
                if current_segment is None:
                    # Bắt đầu segment mới
                    current_segment = {
                        'start_frame': frame,
                        'end_frame': frame,
                        'confidences': [det['confidence']],
                        'bboxes': [det['bbox']],
                        'class_id': class_id,
                        'class_name': class_name
                    }
                elif frame - current_segment['end_frame'] <= GAP_TOLERANCE_FRAMES:
                    # Tiếp tục segment hiện tại (cho phép gap nhỏ)
                    current_segment['end_frame'] = frame
                    current_segment['confidences'].append(det['confidence'])
                    current_segment['bboxes'].append(det['bbox'])
                else:
                    # Kết thúc segment hiện tại và bắt đầu segment mới
                    segments.append(current_segment)
                    current_segment = {
                        'start_frame': frame,
                        'end_frame': frame,
                        'confidences': [det['confidence']],
                        'bboxes': [det['bbox']],
                        'class_id': class_id,
                        'class_name': class_name
                    }
            
            # Thêm segment cuối cùng
            if current_segment is not None:
                segments.append(current_segment)
            
            # Lọc và lưu các segments có thời lượng đủ dài
            for segment in segments:
                duration = (segment['end_frame'] - segment['start_frame']) / fps
                if duration >= MIN_APPEARANCE_DURATION:
                    self._save_detected_sign_for_video(detection, segment, fps)
    
    def _save_detected_sign_for_video(self, detection, sign_data, fps):
        """Lưu một DetectedSign cho video"""
        class_id = sign_data['class_id']
        class_name = sign_data['class_name']
        
        # Tính thời gian và confidence trung bình
        start_time = sign_data['start_frame'] / fps if fps > 0 else 0
        end_time = sign_data['end_frame'] / fps if fps > 0 else 0
        avg_confidence = sum(sign_data['confidences']) / len(sign_data['confidences']) if sign_data['confidences'] else 0
        
        # Lấy bbox cuối cùng (hoặc có thể tính trung bình)
        last_bbox = sign_data['bboxes'][-1] if sign_data['bboxes'] else []
        
        # Tìm TrafficSign tương ứng
        traffic_sign = self._find_traffic_sign(class_id, class_name)
        
        DetectedSign.objects.create(
            detection=detection,
            traffic_sign=traffic_sign,
            class_id=class_id,
            class_name=class_name,
            confidence=avg_confidence,
            bbox=last_bbox,
            start_time=start_time,
            end_time=end_time,
            frame_index=sign_data['start_frame']
        )
    
    def _find_traffic_sign(self, class_id, class_name):
        """Tìm TrafficSign dựa trên class_id hoặc class_name từ YOLO"""
        traffic_sign = None
        
        # Thử tìm theo model_class_id trước
        if class_id is not None:
            traffic_sign = TrafficSign.objects.filter(model_class_id=str(class_id)).first()
        
        # Nếu không tìm thấy, thử tìm theo tên
        if not traffic_sign and class_name:
            traffic_sign = TrafficSign.objects.filter(name__icontains=class_name).first()
        
        return traffic_sign


class DetectionDetailView(generics.RetrieveAPIView):
    """
    API endpoint để xem chi tiết một detection
    
    GET /api/recognition/detection/<id>/
    """
    queryset = Detection.objects.all()
    serializer_class = DetectionDetailSerializer
    permission_classes = [AllowAny]


class RecognitionHistoryListView(generics.ListAPIView):
    """
    API endpoint để xem lịch sử nhận diện (legacy)
    
    GET /api/recognition/history/
    """
    serializer_class = RecognitionHistorySerializer
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return RecognitionHistory.objects.filter(user=self.request.user)
        return RecognitionHistory.objects.none()
