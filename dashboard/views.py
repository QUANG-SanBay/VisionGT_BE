from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated # <-- Permission quan trọng
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Q, Max
from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser
from recognition.models import Detection, DetectedSign, RecognitionHistory
from traffic_signs.models import TrafficSign
from .serializers import (
    UserManagementSerializer,
    DashboardStatsSerializer,
    RecentDetectionSerializer,
    TopDetectedSignSerializer,
    UserActivitySerializer,
    DailyStatsSerializer
)


# Create your views here.
class UserManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]  # Chỉ admin mới có quyền truy cập vào ViewSet này
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserManagementSerializer
    # http_method_names = ['get', 'post', 'put', 'patch', 'delete']  # Cho phép tất cả các phương thức HTTP cần thiết

    # Trả về danh sách user kèm message
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['message'] = 'Lấy danh sách người dùng thành công.'
            response.data['users'] = response.data.pop('results', [])
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Lấy danh sách người dùng thành công.',
            'users': serializer.data
        }, status=status.HTTP_200_OK)

    # Trả về chi tiết user kèm message
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'message': 'Lấy thông tin người dùng thành công.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    # Tạo user mới và trả về user kèm message
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'message': 'Tạo người dùng thành công.',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    # Cập nhật user (PUT/PATCH) và trả về user kèm message
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'message': 'Cập nhật người dùng thành công.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    # Xóa user và trả về message
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = instance.id
        self.perform_destroy(instance)
        return Response({
            'message': f'Xóa người dùng {user_id} thành công.'
        }, status=status.HTTP_200_OK)

    # Vô hiệu hóa tài khoản
    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, *args, **kwargs):
        user = self.get_object()
        if not user.is_active:
            serializer = self.get_serializer(user)
            return Response({
                'message': 'Tài khoản đã ở trạng thái vô hiệu hóa.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

        user.is_active = False
        user.save(update_fields=['is_active'])
        serializer = self.get_serializer(user)
        return Response({
            'message': 'Vô hiệu hóa tài khoản thành công.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    # Kích hoạt tài khoản
    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_active:
            serializer = self.get_serializer(user)
            return Response({
                'message': 'Tài khoản đã ở trạng thái kích hoạt.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

        user.is_active = True
        user.save(update_fields=['is_active'])
        serializer = self.get_serializer(user)
        return Response({
            'message': 'Kích hoạt tài khoản thành công.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


# ==================== DASHBOARD STATISTICS APIs ====================

class DashboardStatsView(APIView):
    """
    API endpoint cho thống kê tổng quan dashboard
    GET /api/dashboard/stats/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Thống kê users
        total_users = CustomUser.objects.count()
        total_customers = CustomUser.objects.filter(role='customer').count()
        total_admins = CustomUser.objects.filter(role='admin').count()

        # Thống kê detections
        total_detections = Detection.objects.count()
        pending_detections = Detection.objects.filter(status='pending').count()
        processing_detections = Detection.objects.filter(status='processing').count()
        done_detections = Detection.objects.filter(status='done').count()
        failed_detections = Detection.objects.filter(status='failed').count()

        # Thống kê theo loại file
        image_detections = Detection.objects.filter(file_type='image').count()
        video_detections = Detection.objects.filter(file_type='video').count()

        # Thống kê traffic signs
        total_traffic_signs = TrafficSign.objects.count()
        total_detected_signs = DetectedSign.objects.count()

        stats_data = {
            'total_users': total_users,
            'total_customers': total_customers,
            'total_admins': total_admins,
            'total_detections': total_detections,
            'total_traffic_signs': total_traffic_signs,
            'total_detected_signs': total_detected_signs,
            'pending_detections': pending_detections,
            'processing_detections': processing_detections,
            'done_detections': done_detections,
            'failed_detections': failed_detections,
            'image_detections': image_detections,
            'video_detections': video_detections,
        }

        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecentDetectionsView(APIView):
    """
    API endpoint cho các detection gần đây
    GET /api/dashboard/recent-detections/?limit=10
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        
        recent_detections = Detection.objects.select_related('user').annotate(
            detected_signs_count=Count('detected_signs')
        ).order_by('-created_at')[:limit]

        data = []
        for detection in recent_detections:
            data.append({
                'id': detection.id,
                'file_type': detection.file_type,
                'status': detection.status,
                'user_email': detection.user.email if detection.user else 'Anonymous',
                'created_at': detection.created_at,
                'detected_signs_count': detection.detected_signs_count
            })

        serializer = RecentDetectionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TopDetectedSignsView(APIView):
    """
    API endpoint cho các biển báo được phát hiện nhiều nhất
    GET /api/dashboard/top-signs/?limit=10
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        
        top_signs = DetectedSign.objects.filter(
            traffic_sign__isnull=False
        ).values(
            'traffic_sign__sign_Code',
            'traffic_sign__name',
            'traffic_sign__category'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

        data = []
        for sign in top_signs:
            data.append({
                'sign_code': sign['traffic_sign__sign_Code'],
                'sign_name': sign['traffic_sign__name'],
                'category': sign['traffic_sign__category'],
                'count': sign['count']
            })

        serializer = TopDetectedSignSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserActivityView(APIView):
    """
    API endpoint cho hoạt động người dùng
    GET /api/dashboard/user-activity/?limit=10
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        
        active_users = CustomUser.objects.annotate(
            total_detections=Count('detection'),
            last_activity=Max('detection__created_at')
        ).filter(
            total_detections__gt=0
        ).order_by('-last_activity')[:limit]

        data = []
        for user in active_users:
            data.append({
                'user_id': user.id,
                'user_email': user.email,
                'full_name': user.get_full_name() or user.username,
                'total_detections': user.total_detections,
                'last_activity': user.last_activity
            })

        serializer = UserActivitySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DailyStatsView(APIView):
    """
    API endpoint cho thống kê theo ngày
    GET /api/dashboard/daily-stats/?days=7
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now().date() - timedelta(days=days-1)
        
        # Lấy dữ liệu cho mỗi ngày
        data = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            detections_count = Detection.objects.filter(
                created_at__date=current_date
            ).count()
            
            new_users_count = CustomUser.objects.filter(
                date_joined__date=current_date
            ).count()
            
            detected_signs_count = DetectedSign.objects.filter(
                created_at__date=current_date
            ).count()
            
            data.append({
                'date': current_date,
                'detections_count': detections_count,
                'new_users_count': new_users_count,
                'detected_signs_count': detected_signs_count
            })

        serializer = DailyStatsSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetectionsByCategoryView(APIView):
    """
    API endpoint cho thống kê detection theo category của biển báo
    GET /api/dashboard/detections-by-category/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        category_stats = DetectedSign.objects.filter(
            traffic_sign__isnull=False
        ).values(
            'traffic_sign__category'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        data = {
            item['traffic_sign__category']: item['count']
            for item in category_stats
        }

        return Response(data, status=status.HTTP_200_OK)


class SystemHealthView(APIView):
    """
    API endpoint cho tình trạng hệ thống
    GET /api/dashboard/system-health/
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Tính toán các chỉ số sức khỏe hệ thống
        total_detections = Detection.objects.count()
        failed_detections = Detection.objects.filter(status='failed').count()
        
        success_rate = 0
        if total_detections > 0:
            success_rate = ((total_detections - failed_detections) / total_detections) * 100

        # Detections trong 24h qua
        last_24h = timezone.now() - timedelta(hours=24)
        detections_24h = Detection.objects.filter(created_at__gte=last_24h).count()
        
        # Active users trong 7 ngày qua
        last_7d = timezone.now() - timedelta(days=7)
        active_users_7d = CustomUser.objects.filter(
            detection__created_at__gte=last_7d
        ).distinct().count()

        data = {
            'success_rate': round(success_rate, 2),
            'total_detections': total_detections,
            'failed_detections': failed_detections,
            'detections_last_24h': detections_24h,
            'active_users_last_7d': active_users_7d,
            'total_traffic_signs': TrafficSign.objects.count(),
            'system_status': 'healthy' if success_rate >= 95 else 'degraded' if success_rate >= 80 else 'critical'
        }

        return Response(data, status=status.HTTP_200_OK)