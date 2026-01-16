from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserManagementViewSet,
    DashboardStatsView,
    RecentDetectionsView,
    TopDetectedSignsView,
    UserActivityView,
    DailyStatsView,
    DetectionsByCategoryView,
    SystemHealthView
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user-management')

urlpatterns = [
    path('', include(router.urls)),
    
    # Dashboard Statistics APIs
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('recent-detections/', RecentDetectionsView.as_view(), name='recent-detections'),
    path('top-signs/', TopDetectedSignsView.as_view(), name='top-detected-signs'),
    path('user-activity/', UserActivityView.as_view(), name='user-activity'),
    path('daily-stats/', DailyStatsView.as_view(), name='daily-stats'),
    path('detections-by-category/', DetectionsByCategoryView.as_view(), name='detections-by-category'),
    path('system-health/', SystemHealthView.as_view(), name='system-health'),
]