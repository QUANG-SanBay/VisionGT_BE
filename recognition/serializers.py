from rest_framework import serializers
from .models import Detection, DetectedSign, RecognitionHistory, RecognitionResult
from traffic_signs.models import TrafficSign


class TrafficSignSerializer(serializers.ModelSerializer):
    """Serializer cho thông tin biển báo"""
    class Meta:
        model = TrafficSign
        fields = [
            'sign_Code', 'name', 'description', 'category',
            'image_url', 'penalty_details', 'model_class_id'
        ]


class DetectedSignSerializer(serializers.ModelSerializer):
    """Serializer cho biển báo được phát hiện"""
    traffic_sign = TrafficSignSerializer(read_only=True)
    
    class Meta:
        model = DetectedSign
        fields = [
            'id', 'class_id', 'class_name', 'confidence', 'bbox',
            'start_time', 'end_time', 'frame_index', 'traffic_sign'
        ]


class DetectionSerializer(serializers.ModelSerializer):
    """Serializer cho Detection - dùng để tạo mới"""
    class Meta:
        model = Detection
        fields = ['id', 'file', 'file_type', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']


class DetectionSummarySerializer(serializers.ModelSerializer):
    """Serializer tóm tắt cho Detection sau khi upload - chỉ thông tin cơ bản"""
    signs_summary = serializers.SerializerMethodField()
    output_file = serializers.SerializerMethodField()
    
    class Meta:
        model = Detection
        fields = [
            'id', 'output_file', 'file_type', 'status', 
            'fps', 'duration', 'created_at', 'signs_summary'
        ]
        read_only_fields = ['id', 'output_file', 'status', 'fps', 'duration', 'created_at']
    
    def get_output_file(self, obj):
        """Trả về URL đầy đủ cho output file qua endpoint serve media"""
        if obj.output_file:
            request = self.context.get('request')
            if request:
                # Sử dụng endpoint serve media với proper headers
                file_path = obj.output_file.name  # Lấy path tương đối
                return request.build_absolute_uri(f'/api/recognition/media/{file_path}')
        return None
    
    def get_signs_summary(self, obj):
        """Tóm tắt cơ bản: tên biển, số lần xuất hiện, tỉ lệ confidence trung bình, và timeline xuất hiện"""
        signs = obj.detected_signs.all()
        summary = {}
        for sign in signs:
            if sign.class_name not in summary:
                summary[sign.class_name] = {
                    'count': 0,
                    'total_duration': 0,
                    'confidences': [],
                    'appearances': []  # Danh sách các lần xuất hiện
                }
            summary[sign.class_name]['count'] += 1
            
            # Thêm thông tin appearance
            appearance = {
                'confidence': round(sign.confidence, 3)
            }
            
            if sign.start_time is not None and sign.end_time is not None:
                duration = sign.end_time - sign.start_time
                summary[sign.class_name]['total_duration'] += duration
                appearance['start_time'] = round(sign.start_time, 3)
                appearance['end_time'] = round(sign.end_time, 3)
                appearance['duration'] = round(duration, 3)
            elif sign.frame_index is not None:
                # Cho ảnh, chỉ có frame_index
                appearance['frame_index'] = sign.frame_index
            
            summary[sign.class_name]['appearances'].append(appearance)
            summary[sign.class_name]['confidences'].append(sign.confidence)
        
        # Tính confidence trung bình và làm tròn
        for sign_name, data in summary.items():
            confidences = data['confidences']
            data['avg_confidence'] = round(sum(confidences) / len(confidences), 3) if confidences else 0
            data['total_duration'] = round(data['total_duration'], 2)
            del data['confidences']  # Xóa list gốc
        
        return summary


class DetectionDetailSerializer(serializers.ModelSerializer):
    """Serializer chi tiết cho Detection - bao gồm các biển báo phát hiện được (unique only)"""
    detected_signs = serializers.SerializerMethodField()
    signs_summary = serializers.SerializerMethodField()
    output_file = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    
    class Meta:
        model = Detection
        fields = [
            'id', 'file', 'output_file', 'file_type', 
            'status', 'fps', 'duration', 'total_frames', 
            'error_message', 'created_at', 'detected_signs', 'signs_summary'
        ]
        read_only_fields = [
            'id', 'output_file', 'status', 'fps', 'duration', 
            'total_frames', 'error_message', 'created_at'
        ]
    
    def get_detected_signs(self, obj):
        """
        Trả về danh sách biển báo unique (không trùng lặp)
        Mỗi loại biển báo chỉ xuất hiện 1 lần, lấy detection có confidence cao nhất
        """
        signs = obj.detected_signs.all()
        
        # Group theo class_name và lấy detection có confidence cao nhất
        unique_signs = {}
        for sign in signs:
            if sign.class_name not in unique_signs:
                unique_signs[sign.class_name] = sign
            else:
                # So sánh confidence, giữ lại cái có confidence cao hơn
                if sign.confidence > unique_signs[sign.class_name].confidence:
                    unique_signs[sign.class_name] = sign
        
        # Serialize các signs unique
        return DetectedSignSerializer(
            list(unique_signs.values()), 
            many=True,
            context=self.context
        ).data
    
    def get_file(self, obj):
        """Trả về URL đầy đủ cho input file"""
        if obj.file:
            request = self.context.get('request')
            if request:
                file_path = obj.file.name
                return request.build_absolute_uri(f'/api/recognition/media/{file_path}')
        return None
    
    def get_output_file(self, obj):
        """Trả về URL đầy đủ cho output file qua endpoint serve media"""
        if obj.output_file:
            request = self.context.get('request')
            if request:
                file_path = obj.output_file.name
                return request.build_absolute_uri(f'/api/recognition/media/{file_path}')
        return None
    
    def get_signs_summary(self, obj):
        """Tóm tắt số lượng từng loại biển báo với timeline chi tiết"""
        signs = obj.detected_signs.all()
        summary = {}
        for sign in signs:
            if sign.class_name not in summary:
                summary[sign.class_name] = {
                    'count': 0,
                    'total_duration': 0,
                    'confidences': [],
                    'appearances': []  # Danh sách các lần xuất hiện
                }
            summary[sign.class_name]['count'] += 1
            
            # Thêm thông tin appearance
            appearance = {
                'confidence': round(sign.confidence, 3)
            }
            
            if sign.start_time is not None and sign.end_time is not None:
                duration = sign.end_time - sign.start_time
                summary[sign.class_name]['total_duration'] += duration
                appearance['start_time'] = round(sign.start_time, 3)
                appearance['end_time'] = round(sign.end_time, 3)
                appearance['duration'] = round(duration, 3)
            elif sign.frame_index is not None:
                # Cho ảnh, chỉ có frame_index
                appearance['frame_index'] = sign.frame_index
            
            summary[sign.class_name]['appearances'].append(appearance)
            summary[sign.class_name]['confidences'].append(sign.confidence)
        
        # Tính confidence trung bình và làm tròn
        for sign_name, data in summary.items():
            confidences = data['confidences']
            data['avg_confidence'] = round(sum(confidences) / len(confidences), 3) if confidences else 0
            data['total_duration'] = round(data['total_duration'], 2)
            del data['confidences']  # Xóa list gốc
        
        return summary


class RecognitionResultSerializer(serializers.ModelSerializer):
    """Serializer cho kết quả nhận diện (legacy model)"""
    traffic_sign = TrafficSignSerializer(read_only=True)
    
    class Meta:
        model = RecognitionResult
        fields = ['id', 'bounding_box', 'confidence_score', 'traffic_sign']


class RecognitionHistorySerializer(serializers.ModelSerializer):
    """Serializer cho lịch sử nhận diện (legacy model)"""
    results = RecognitionResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecognitionHistory
        fields = [
            'id', 'timestamp', 'input_image_url', 
            'ouput_image_url', 'user', 'results'
        ]
        read_only_fields = ['id', 'timestamp']
