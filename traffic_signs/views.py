from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q

from .models import TrafficSign
from .serializers import TrafficSignSerializer, TrafficSignListSerializer


class IsAdminUser(IsAuthenticated):
    """
    Custom permission: Chỉ admin (role='admin') mới được phép
    """
    def has_permission(self, request, view):
        # Kiểm tra đăng nhập trước
        if not super().has_permission(request, view):
            return False
        # Kiểm tra role
        return request.user.role == 'admin'


class TrafficSignViewSet(viewsets.ModelViewSet):
    """
    ViewSet quản lý biển báo giao thông (Admin only)
    
    - list: GET /api/traffic-signs/ (Admin - xem danh sách)
    - retrieve: GET /api/traffic-signs/{sign_Code}/ (Admin - xem chi tiết)
    - create: POST /api/traffic-signs/ (Admin - tạo mới)
    - update: PUT /api/traffic-signs/{sign_Code}/ (Admin - cập nhật)
    - partial_update: PATCH /api/traffic-signs/{sign_Code}/ (Admin - cập nhật một phần)
    - destroy: DELETE /api/traffic-signs/{sign_Code}/ (Admin - xóa)
    - search: GET /api/traffic-signs/search/?q=keyword (Admin - tìm kiếm)
    """
    queryset = TrafficSign.objects.all().order_by('-created_at')
    lookup_field = 'sign_Code'  # Sử dụng sign_Code thay vì pk
    
    def get_serializer_class(self):
        """Sử dụng serializer khác nhau cho list và detail"""
        if self.action == 'list':
            return TrafficSignListSerializer
        return TrafficSignSerializer
    
    def get_permissions(self):
        """
        Phân quyền: Tất cả endpoints đều yêu cầu Admin
        """
        permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/traffic-signs/
        Lấy danh sách tất cả biển báo
        """
        queryset = self.get_queryset()
        
        # Filter theo category nếu có
        category = request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/traffic-signs/{sign_Code}/
        Xem chi tiết một biển báo
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/traffic-signs/
        Tạo mới biển báo (Admin only)
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Tạo biển báo thành công.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Tạo biển báo thất bại.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/traffic-signs/{sign_Code}/
        Cập nhật đầy đủ biển báo (Admin only)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Cập nhật biển báo thành công.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Cập nhật biển báo thất bại.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/traffic-signs/{sign_Code}/
        Cập nhật một phần biển báo (Admin only)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Cập nhật biển báo thành công.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Cập nhật biển báo thất bại.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/traffic-signs/{sign_Code}/
        Xóa biển báo (Admin only)
        """
        instance = self.get_object()
        sign_code = instance.sign_Code
        instance.delete()
        return Response({
            'success': True,
            'message': f'Đã xóa biển báo {sign_code}.'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        GET /api/traffic-signs/search/?q=keyword (Admin)
        Tìm kiếm biển báo theo tên hoặc mã
        """
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({
                'success': False,
                'message': 'Vui lòng nhập từ khóa tìm kiếm.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Tìm kiếm theo sign_Code hoặc name
        queryset = self.get_queryset().filter(
            Q(sign_Code__icontains=query) | 
            Q(name__icontains=query)
        )
        
        serializer = TrafficSignListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'query': query,
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        GET /api/traffic-signs/categories/ (Admin)
        Lấy danh sách các danh mục biển báo
        """
        categories = TrafficSign.objects.values_list('category', flat=True).distinct()
        return Response({
            'success': True,
            'count': len(categories),
            'data': list(categories)
        }, status=status.HTTP_200_OK)
