import os
import logging
import mimetypes
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.http import FileResponse, Http404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny

from .models import Detection, DetectedSign, RecognitionHistory
from .serializers import (
    DetectionSerializer,
    DetectionSummarySerializer,
    DetectionDetailSerializer,
    RecognitionHistorySerializer
)
from traffic_signs.models import TrafficSign
from ai_engine.yolo_infer import predict_image_with_save, predict_video_with_save
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class DetectionUploadRunView(generics.CreateAPIView):
    """
    API endpoint để upload hình ảnh/video và chạy nhận diện biển báo
    Yêu cầu đăng nhập
    
    POST /api/recognition/upload-run/
    Form-data:
        - file: file upload (image hoặc video)
        - file_type: "image" hoặc "video"
    
    Response (Summary):
        {
            "success": true,
            "message": "Nhận diện thành công",
            "detection_id": 123,
            "file_type": "video",
            "data": {
                "id": 123,
                "output_file": "http://...",
                "file_type": "video",
                "status": "done",
                "fps": 30.0,
                "duration": 10.5,
                "created_at": "...",
                "signs_summary": {
                    "Cấm rẽ trái": {
                        "count": 3,
                        "total_duration": 5.2,
                        "avg_confidence": 0.89
                    }
                }
            }
        }
    """
    serializer_class = DetectionSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]  # Yêu cầu đăng nhập
    
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
            user=request.user  # Lưu user đã đăng nhập
        )
        
        try:
            # Lấy đường dẫn file đã upload
            file_path = Path(detection.file.path)
            
            if file_type == 'image':
                # Xử lý ảnh với confidence threshold 0.5
                detections, output_path = predict_image_with_save(file_path, conf=0.5)
                
                # Lọc overlapping detections
                detections = self._filter_overlapping_detections(detections)
                
                # Lưu output file
                with open(output_path, 'rb') as f:
                    detection.output_file.save(output_path.name, File(f), save=False)
                
                # Tạo DetectedSign cho ảnh
                self._create_detected_signs_for_image(detection, detections)
                
            else:  # video
                # Xử lý video với confidence threshold 0.5
                frame_detections, output_path, fps = predict_video_with_save(file_path, conf=0.5)
                
                # Lọc overlapping detections cho từng frame
                for frame_data in frame_detections:
                    frame_data['detections'] = self._filter_overlapping_detections(frame_data['detections'])
                
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
            
            # Trả về response với thông tin tóm tắt
            serializer = DetectionSummarySerializer(detection, context={'request': request})
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
    
    def _calculate_iou(self, box1, box2):
        """Tính Intersection over Union (IoU) giữa 2 bounding boxes"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Tính diện tích giao nhau
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Tính diện tích hợp nhất
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def _filter_overlapping_detections(self, detections, iou_threshold=0.5):
        """
        Lọc các detections bị overlap (Non-Maximum Suppression)
        Chỉ giữ detection có confidence cao nhất trong nhóm overlap
        """
        if not detections:
            return detections
        
        # Sắp xếp theo confidence giảm dần
        sorted_dets = sorted(detections, key=lambda x: x.get('confidence', 0), reverse=True)
        
        filtered = []
        skip_indices = set()
        
        for i, det1 in enumerate(sorted_dets):
            if i in skip_indices:
                continue
            
            filtered.append(det1)
            bbox1 = det1.get('bbox', [])
            
            if len(bbox1) != 4:
                continue
            
            # So sánh với các detections còn lại
            for j in range(i + 1, len(sorted_dets)):
                if j in skip_indices:
                    continue
                
                det2 = sorted_dets[j]
                bbox2 = det2.get('bbox', [])
                
                if len(bbox2) != 4:
                    continue
                
                # Tính IoU
                iou = self._calculate_iou(bbox1, bbox2)
                
                # Nếu overlap quá nhiều, bỏ detection có confidence thấp hơn
                if iou > iou_threshold:
                    skip_indices.add(j)
        
        return filtered
    
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
    API endpoint để xem chi tiết đầy đủ một detection
    Yêu cầu đăng nhập và chỉ xem được detection của chính mình
    
    GET /api/recognition/detection/<id>/
    """
    serializer_class = DetectionDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Chỉ cho phép user xem detection của chính mình
        return Detection.objects.filter(user=self.request.user)


class RecognitionHistoryListView(generics.ListAPIView):
    """
    API endpoint để xem danh sách lịch sử nhận diện (Detection)
    Yêu cầu đăng nhập và chỉ xem được lịch sử của chính mình
    
    GET /api/recognition/history/
    
    Response: Danh sách các detection đã thực hiện (thông tin tóm tắt)
    """
    serializer_class = DetectionSummarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Trả về danh sách detection của user, sắp xếp mới nhất trước
        return Detection.objects.filter(user=self.request.user).order_by('-created_at')


class ServeMediaFileView(APIView):
    """
    API endpoint để serve media files (video/image) với proper headers cho streaming
    GET /api/recognition/media/<path:file_path>
    """
    permission_classes = [AllowAny]  # Có thể thêm authentication nếu cần
    
    def get(self, request, file_path):
        # Xây dựng đường dẫn file đầy đủ
        media_root = Path(settings.MEDIA_ROOT)
        full_path = media_root / file_path
        
        # Kiểm tra file tồn tại và nằm trong MEDIA_ROOT
        if not full_path.exists() or not full_path.is_file():
            raise Http404("File not found")
        
        # Kiểm tra file nằm trong MEDIA_ROOT (security)
        try:
            full_path.resolve().relative_to(media_root.resolve())
        except ValueError:
            raise Http404("Access denied")
        
        # Xác định MIME type
        mime_type, _ = mimetypes.guess_type(str(full_path))
        if not mime_type:
            if full_path.suffix.lower() in ['.mp4', '.avi', '.mov']:
                mime_type = 'video/mp4'
            elif full_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                mime_type = 'image/jpeg'
            else:
                mime_type = 'application/octet-stream'
        
        # Mở file và tạo response
        try:
            response = FileResponse(
                open(full_path, 'rb'),
                content_type=mime_type
            )
            
            # Thêm headers cho video streaming
            file_size = full_path.stat().st_size
            response['Content-Length'] = file_size
            response['Accept-Ranges'] = 'bytes'
            
            # Xử lý Range request cho video streaming
            range_header = request.META.get('HTTP_RANGE', '')
            if range_header:
                range_match = range_header.replace('bytes=', '').split('-')
                start = int(range_match[0]) if range_match[0] else 0
                end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1
                
                response = FileResponse(
                    open(full_path, 'rb'),
                    content_type=mime_type,
                    status=206  # Partial Content
                )
                response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                response['Content-Length'] = end - start + 1
                response['Accept-Ranges'] = 'bytes'
            
            # Cache control
            response['Cache-Control'] = 'public, max-age=3600'
            
            return response
            
        except Exception as e:
            logger.error(f"Error serving file {file_path}: {str(e)}")
            raise Http404("Error serving file")