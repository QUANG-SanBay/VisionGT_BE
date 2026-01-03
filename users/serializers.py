from rest_framework import serializers
import uuid
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True) # Confirm password field
    full_name = serializers.CharField(max_length=100, write_only=True) # Full name field
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def validate(self, attrs):
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Email đã được sử dụng.'})
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Mật khẩu không khớp.'})
        return attrs
    def save(self):
        # Lấy dữ liệu đã được validate
        validated_data = self.validated_data
        
        # Tách full_name thành first_name và last_name
        full_name = validated_data.get('full_name')
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Tự động tạo một username duy nhất từ email
        # Ví dụ: 'test@example.com' -> 'test'
        # Thêm một chuỗi ngẫu nhiên để đảm bảo duy nhất
        base_username = validated_data['email'].split('@')[0]
        random_suffix = uuid.uuid4().hex[:6]
        username = f"{base_username}_{random_suffix}"
        
        # Đảm bảo username này chắc chắn là duy nhất
        while CustomUser.objects.filter(username=username).exists():
            random_suffix = uuid.uuid4().hex[:6]
            username = f"{base_username}_{random_suffix}"
        
        # Tạo đối tượng user
        user = CustomUser(
            username=username,
            email=validated_data['email'],
            first_name=first_name,
            last_name=last_name
        )
        
        password = validated_data['password']
        # password2 = validated_data['password2']
        # if password != password2:
        #     raise serializers.ValidationError({'password': 'Mật khẩu không khớp.'})
        user.set_password(password)
        user.save()
        return user
# class loginSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(max_length=100)
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'password']
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }
#     def validate(self, attrs):
#         #nếu email không tồn tại trong db thì báo lỗi
#         if not CustomUser.objects.filter(email=attrs['email']).exists():
#             raise serializers.ValidationError({'email': 'Email không tồn tại.'})
#         return attrs
#     def submit(self):
#         validated_data = self.validated_data
#         email = validated_data['email']
#         password = validated_data['password']
#         user = CustomUser.objects.get(email=email)
#         if not user.check_password(password):
#             raise serializers.ValidationError({'password': 'Mật khẩu không đúng.'})
#         return user
    