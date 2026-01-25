import uuid
from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer cho thống kê tổng quan dashboard"""
    total_users = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_admins = serializers.IntegerField()
    total_detections = serializers.IntegerField()
    total_traffic_signs = serializers.IntegerField()
    total_detected_signs = serializers.IntegerField()
    
    # Thống kê theo trạng thái
    pending_detections = serializers.IntegerField()
    processing_detections = serializers.IntegerField()
    done_detections = serializers.IntegerField()
    failed_detections = serializers.IntegerField()
    
    # Thống kê theo loại file
    image_detections = serializers.IntegerField()
    video_detections = serializers.IntegerField()


class RecentDetectionSerializer(serializers.Serializer):
    """Serializer cho các detection gần đây"""
    id = serializers.IntegerField()
    file_type = serializers.CharField()
    status = serializers.CharField()
    user_email = serializers.EmailField()
    created_at = serializers.DateTimeField()
    detected_signs_count = serializers.IntegerField()


class TopDetectedSignSerializer(serializers.Serializer):
    """Serializer cho các biển báo được phát hiện nhiều nhất"""
    sign_code = serializers.CharField()
    sign_name = serializers.CharField()
    category = serializers.CharField()
    count = serializers.IntegerField()


class UserActivitySerializer(serializers.Serializer):
    """Serializer cho hoạt động người dùng"""
    user_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    full_name = serializers.CharField()
    total_detections = serializers.IntegerField()
    last_activity = serializers.DateTimeField()


class DailyStatsSerializer(serializers.Serializer):
    """Serializer cho thống kê theo ngày"""
    date = serializers.DateField()
    detections_count = serializers.IntegerField()
    new_users_count = serializers.IntegerField()
    detected_signs_count = serializers.IntegerField() # import serializers dùng để tạo serializer
from rest_framework.validators import UniqueValidator # import UniqueValidator để kiểm tra tính duy nhất của trường email
from rest_framework import exceptions # import exceptions để xử lý ngoại lệ

from users.models import CustomUser

class UserManagementSerializer(serializers.ModelSerializer):
    # khai báo các trường cần thiết cho serializer 
    full_name = serializers.SerializerMethodField(read_only=True)  # Trường full_name được tính toán từ first_name và last_name
    input_full_name = serializers.CharField(write_only=True, required=False)  # Trường input_full_name để nhận dữ liệu từ client
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=False)  # Trường xác nhận mật khẩu

     # Phương thức để tách full_name thành first_name và last_name
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'input_full_name', 'gender', 'is_active', 'is_staff', 'role', 'password', 'password2']
        read_only_fields = ['id', 'username']
        #password chỉ dùng để tạo mới user, không bắt buộc khi cập nhật
        extra_kwargs = {
            'password2': {'write_only': True, 'required': False},
            'password': {'write_only': True, 'required': False}
        }
    
    ###PHẦN ĐỌC###
    # Phương thức để lấy full_name từ first_name và last_name
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    ###PHẦN GHI###
    def _split_full_name(self, full_name):
        """Hàm trợ giúp để tách full_name."""
        parts = full_name.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name

    def validate(self, data):
        """Validate dữ liệu - chỉ bắt buộc password khi tạo mới"""
        # Nếu đang tạo mới (không có instance)
        if not self.instance:
            if not data.get('password'):
                raise serializers.ValidationError({'password': 'Mật khẩu là bắt buộc khi tạo user mới.'})
            if not data.get('password2'):
                raise serializers.ValidationError({'password2': 'Xác nhận mật khẩu là bắt buộc khi tạo user mới.'})
            if not data.get('input_full_name'):
                raise serializers.ValidationError({'input_full_name': 'Họ tên là bắt buộc khi tạo user mới.'})
        return data

    def create(self, validated_data):
         # Lấy full_name từ dữ liệu đã được validate
        full_name = validated_data.pop('input_full_name', '')
        first_name, last_name = self._split_full_name(full_name)
        # lấy mật khẩu và các trường khác từ validated_data
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        if password != password2:
            raise serializers.ValidationError({'password': 'Mật khẩu không khớp.'})
         # Tạo user với first_name và last_name đã được tách username từ email + _random
        email = validated_data.pop('email')
        base_username = email.split('@')[0]
        random_suffix = uuid.uuid4().hex[:6]
        username = f"{base_username}_{random_suffix}"
        user = CustomUser(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **validated_data
        )
        user.set_password(password)  # Mã hóa mật khẩu
        user.save()
        return user
    
    # Ghi đè phương thức update để xử lý 'input_full_name'
    def update(self, instance, validated_data):
        # instance ở đây là user object hiện tại đang được cập nhật
        # Nếu 'input_full_name' được gửi lên trong payload
        if 'input_full_name' in validated_data:
            full_name = validated_data.pop('input_full_name')
            first_name, last_name = self._split_full_name(full_name)
            instance.first_name = first_name
            instance.last_name = last_name

        # Xử lý đổi password nếu có
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)
        
        if password and password2:
            if password != password2:
                raise serializers.ValidationError({'password': 'Mật khẩu không khớp.'})
            instance.set_password(password)
        elif password or password2:
            raise serializers.ValidationError({'password': 'Cần cung cấp cả password và password2 để đổi mật khẩu.'})

        # Cập nhật các trường còn lại như bình thường
        # super().update() sẽ lặp qua các trường còn lại trong validated_data và gán cho instance
        return super().update(instance, validated_data)
    # xóa đối tượng response message khi xóa user
    def delete(self):
        return {'message': 'User đã được xóa thành công.'}
    
    
    
