from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework import exceptions
import uuid
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all(), lookup='iexact')]
    )
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True) # Confirm password field
    full_name = serializers.CharField(max_length=100, write_only=True) # Full name field
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        attrs['email'] = email
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

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'gender', 'role', 'date_joined']
        read_only_fields = ['id', 'username', 'role', 'date_joined']

    def validate_email(self, value):
        email = value.strip().lower()
        user_qs = CustomUser.objects.filter(email__iexact=email)
        if self.instance:
            user_qs = user_qs.exclude(pk=self.instance.pk)
        if user_qs.exists():
            raise exceptions.ValidationError('Email đã được sử dụng.')
        return email
class ChangeProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    full_name = serializers.CharField(source='get_full_name', required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'gender']
    def validate_email(self, value):
        email = value.strip().lower()
        user_qs = CustomUser.objects.filter(email__iexact=email)
        if self.instance:
            user_qs = user_qs.exclude(pk=self.instance.pk)
        if user_qs.exists():
            raise exceptions.ValidationError('Email đã được sử dụng.')
        return email
    def update(self, instance, validated_data):
        # Cập nhật email nếu có trong validated_data
        email = validated_data.get('email')
        if email:
            instance.email = email

        # Cập nhật full_name nếu có trong validated_data
        full_name = validated_data.get('get_full_name')
        if full_name:
            name_parts = full_name.split(' ', 1)
            instance.first_name = name_parts[0]
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ''
        # Cập nhật gender nếu có trong validated_data
        gender = validated_data.get('gender')   
        if gender is not None:
            instance.gender = gender
        instance.save()
        return instance
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({'new_password': 'Mật khẩu mới không khớp.'})
        return attrs
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Mật khẩu cũ không đúng.')
        return value
