import uuid
from rest_framework import serializers # import serializers dùng để tạo serializer
from rest_framework.validators import UniqueValidator # import UniqueValidator để kiểm tra tính duy nhất của trường email
from rest_framework import exceptions # import exceptions để xử lý ngoại lệ

from users.models import CustomUser

class UserManagementSerializer(serializers.ModelSerializer):
    # khai báo các trường cần thiết cho serializer 
    full_name = serializers.SerializerMethodField(read_only=True)  # Trường full_name được tính toán từ first_name và last_name
    input_full_name = serializers.CharField(write_only=True, required=True)  # Trường input_full_name để nhận dữ liệu từ client
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)  # Trường xác nhận mật khẩu

     # Phương thức để tách full_name thành first_name và last_name
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'input_full_name', 'gender', 'is_active', 'is_staff', 'role', 'password', 'password2']
        read_only_fields = ['id', 'username']
        #password chỉ dùng để tạo mới user, không bắt buộc khi cập nhật
        extra_kwargs = {
            'password2': {'write_only': True, 'required': True},
            'password': {'write_only': True, 'required': True}
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
        base_username = validated_data['email'].split('@')[0]
        random_suffix = uuid.uuid4().hex[:6]
        username = f"{base_username}_{random_suffix}"
        user = CustomUser(
            username=username,
            email=validated_data['email'],
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

        # Cập nhật các trường còn lại như bình thường
        # super().update() sẽ lặp qua các trường còn lại trong validated_data và gán cho instance
        return super().update(instance, validated_data)
    # xóa đối tượng response message khi xóa user
    def delete(self):
        return {'message': 'User đã được xóa thành công.'}
    
    
    
