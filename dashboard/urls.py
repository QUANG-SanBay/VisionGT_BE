from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserManagementViewSet

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user-management')
urlpatterns = [
    path('', include(router.urls)),
    # Thêm các đường dẫn URL cho ứng dụng dashboard tại đây
]