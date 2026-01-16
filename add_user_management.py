# Script to add UserManagementViewSet to users/views.py
import os

views_path = r"D:\Dai_HOC\HK1_2025-2026\HT_GTTM\Project\vision-GT-BE\users\views.py"

# Read current content
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if UserManagementViewSet already exists
if 'class UserManagementViewSet' in content:
    print("UserManagementViewSet already exists!")
else:
    # Append the new code
    new_code = '''

class UserManagementViewSet(viewsets.ViewSet):
    """ViewSet quản lý người dùng (Admin only)"""
    permission_classes = [IsAdminUser]
    
    def list(self, request):
        users = CustomUser.objects.all().order_by('-date_joined')
        role = request.query_params.get('role')
        if role:
            users = users.filter(role=role)
        data = [{'id': u.id, 'username': u.username, 'email': u.email, 'full_name': u.get_full_name(), 'role': u.role, 'gender': u.gender, 'is_active': u.is_active, 'date_joined': u.date_joined} for u in users]
        return Response({'success': True, 'count': len(data), 'data': data})
    
    def retrieve(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            return Response({'success': True, 'data': ProfileSerializer(user).data})
        except CustomUser.DoesNotExist:
            return Response({'success': False, 'message': 'Người dùng không tồn tại.'}, status=404)
    
    @action(detail=True, methods=['patch'])
    def update_role(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            new_role = request.data.get('role')
            if new_role not in ['admin', 'customer']:
                return Response({'success': False, 'message': 'Role không hợp lệ.'}, status=400)
            if user.id == request.user.id:
                return Response({'success': False, 'message': 'Không thể thay đổi role của chính mình.'}, status=400)
            user.role = new_role
            user.is_staff = (new_role == 'admin')
            user.save()
            return Response({'success': True, 'message': 'Đã cập nhật role.'})
        except CustomUser.DoesNotExist:
            return Response({'success': False, 'message': 'Không tồn tại.'}, status=404)
    
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            if user.id == request.user.id:
                return Response({'success': False, 'message': 'Không thể vô hiệu hóa chính mình.'}, status=400)
            user.is_active = not user.is_active
            user.save()
            return Response({'success': True, 'message': 'Đã cập nhật trạng thái.'})
        except CustomUser.DoesNotExist:
            return Response({'success': False, 'message': 'Không tồn tại.'}, status=404)
    
    def destroy(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            if user.id == request.user.id:
                return Response({'success': False, 'message': 'Không thể xóa chính mình.'}, status=400)
            email = user.email
            user.delete()
            return Response({'success': True, 'message': f'Đã xóa {email}.'})
        except CustomUser.DoesNotExist:
            return Response({'success': False, 'message': 'Không tồn tại.'}, status=404)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'success': False, 'message': 'Vui lòng nhập từ khóa.'}, status=400)
        users = CustomUser.objects.filter(Q(email__icontains=query) | Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        data = [{'id': u.id, 'username': u.username, 'email': u.email, 'full_name': u.get_full_name(), 'role': u.role, 'is_active': u.is_active} for u in users]
        return Response({'success': True, 'query': query, 'count': len(data), 'data': data})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        return Response({'success': True, 'data': {'total_users': CustomUser.objects.count(), 'admin_count': CustomUser.objects.filter(role='admin').count(), 'customer_count': CustomUser.objects.filter(role='customer').count(), 'active_users': CustomUser.objects.filter(is_active=True).count(), 'inactive_users': CustomUser.objects.filter(is_active=False).count()}})
'''
    
    # Write back
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content + new_code)
    
    print("UserManagementViewSet added successfully!")
