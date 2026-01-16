from rest_framework import serializers
from .models import TrafficSign


class TrafficSignSerializer(serializers.ModelSerializer):
    """Serializer cho TrafficSign với tất cả thông tin"""
    class Meta:
        model = TrafficSign
        fields = [
            'sign_Code', 'name', 'description', 'category',
            'image_url', 'penalty_details', 'model_class_id',
            'created_at', 'last_updated'
        ]
        read_only_fields = ['created_at', 'last_updated']
    
    def validate_sign_Code(self, value):
        """Validate sign_Code format"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Mã biển báo không được để trống.")
        return value.strip()
    
    def validate_name(self, value):
        """Validate name"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Tên biển báo không được để trống.")
        return value.strip()
    
    def validate_category(self, value):
        """Validate category"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Danh mục không được để trống.")
        return value.strip()


class TrafficSignListSerializer(serializers.ModelSerializer):
    """Serializer rút gọn cho danh sách biển báo"""
    class Meta:
        model = TrafficSign
        fields = [
            'sign_Code', 'name', 'category', 
            'image_url', 'model_class_id'
        ]
