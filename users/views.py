from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import CustomUser
from .serializers import RegisterSerializer, ProfileSerializer, ChangeProfileSerializer, ChangePasswordSerializer

#============================
# Create your views here.
#============================
class registerAPI_view(APIView):
    # ÄÄƒng kÃ½ ngÆ°á»i dÃ¹ng má»›i
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            message = {
                'message': 'User registered successfully.',
                'user': {
                    'email': user.email,
                    'full_name': user.get_full_name(),
                }
                
            }
            return Response(message, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'ÄÄƒng kÃ½ tháº¥t báº¡i.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
#============================
# ÄÄƒng nháº­p vá»›i JWT 
#============================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # ThÃªm cÃ¡c thÃ´ng tin tÃ¹y chá»‰nh vÃ o token
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role  # ThÃªm role vÃ o JWT payload
        return token
# View Ä‘á»ƒ láº¥y token
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as exc:
            return Response({
                'message': 'ÄÄƒng nháº­p tháº¥t báº¡i.',
                'errors': exc.detail,
            }, status=status.HTTP_401_UNAUTHORIZED)
        except ValidationError as exc:
            return Response({
                'message': 'ÄÄƒng nháº­p tháº¥t báº¡i.',
                'errors': exc.detail,
            }, status=status.HTTP_400_BAD_REQUEST)

        tokens = serializer.validated_data
        user = serializer.user
        return Response({
            'message': 'ÄÄƒng nháº­p thÃ nh cÃ´ng.',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'role': user.role,  # ThÃªm role Ä‘á»ƒ FE phÃ¢n quyá»n
            },
            'userToken': {
                'access': tokens.get('access'),
                'refresh': tokens.get('refresh'),
            }
        }, status=status.HTTP_200_OK)

#============================
#logout view
#===========================
class LogoutView(APIView):
    # khi sá»­ dá»¥ng API nÃ y, ngÆ°á»i dÃ¹ng pháº£i Ä‘Æ°á»£c xÃ¡c thá»±c
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() # ÄÆ°a token vÃ o blacklist
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
#============================
# profile view
#===========================
class ProfileView(APIView):
    # khi sá»­ dá»¥ng API nÃ y, ngÆ°á»i dÃ¹ng pháº£i Ä‘Æ°á»£c xÃ¡c thá»±c
    permission_classes = (IsAuthenticated,)
    # Láº¥y thÃ´ng tin profile cá»§a ngÆ°á»i dÃ¹ng hiá»‡n táº¡i
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

#============================
# change profile view
#============================
class ChangeProfileView(APIView):
    # khi sá»­ dá»¥ng API nÃ y, ngÆ°á»i dÃ¹ng pháº£i Ä‘Æ°á»£c xÃ¡c thá»±c
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = ChangeProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully.',
                'user': serializer.data,
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Profile update failed.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
#============================
# change password view
#============================
class ChangePasswordView(APIView):
    # khi sá»­ dá»¥ng API nÃ y, ngÆ°á»i dÃ¹ng pháº£i Ä‘Æ°á»£c xÃ¡c thá»±c
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({
                'message': 'Password changed successfully.',
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Password change failed.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

#===========================
# Login with social accounts (Google / Facebook)
#===========================
class GoogleLogin(SocialLoginView):
    """Nháº­n access_token tá»« frontend, xÃ¡c thá»±c vá»›i Google vÃ  tráº£ JWT há»‡ thá»‘ng."""
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:3000'
    client_class = OAuth2Client


class FacebookLogin(SocialLoginView):
    """Nháº­n access_token tá»« frontend, xÃ¡c thá»±c vá»›i Facebook vÃ  tráº£ JWT há»‡ thá»‘ng."""
    adapter_class = FacebookOAuth2Adapter
    callback_url = 'http://localhost:3000'
    client_class = OAuth2Client

#============================
# Admin - QuảnAnonymous người dùng
#============================
class IsAdminUser(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view): return False
        return request.user.role == 'admin'



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
