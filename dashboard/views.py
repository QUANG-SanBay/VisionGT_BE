from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser # <-- Permission quan trọng
from users.models import CustomUser
from .serializers import UserManagementSerializer


# Create your views here.
class UserManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]  # Chỉ admin mới có quyền truy cập vào ViewSet này
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserManagementSerializer
    # http_method_names = ['get', 'post', 'put', 'patch', 'delete']  # Cho phép tất cả các phương thức HTTP cần thiết
    