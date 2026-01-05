from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser # <-- Permission quan trọng
from rest_framework.response import Response
from rest_framework.decorators import action
from users.models import CustomUser
from .serializers import UserManagementSerializer


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
    