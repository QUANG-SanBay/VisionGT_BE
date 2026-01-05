from rest_framework import serializers # import serializers dùng để tạo serializer
from rest_framework.validators import UniqueValidator # import UniqueValidator để kiểm tra tính duy nhất của trường email
from rest_framework import exceptions # import exceptions để xử lý ngoại lệ

from users.models import CustomUser

class UserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        read_only_fields = ['id', 'username']
        
