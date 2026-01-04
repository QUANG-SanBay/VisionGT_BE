from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer, ProfileSerializer, ChangeProfileSerializer, ChangePasswordSerializer

#============================
# Create your views here.
#============================
class registerAPI_view(APIView):
    # Đăng ký người dùng mới
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
            'message': 'Đăng ký thất bại.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
#============================
# Đăng nhập với JWT 
#============================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Thêm các thông tin tùy chỉnh vào token nếu muốn
        # Ví dụ: thêm username và email
        token['username'] = user.username
        token['email'] = user.email
        return token
# View để lấy token
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as exc:
            return Response({
                'message': 'Đăng nhập thất bại.',
                'errors': exc.detail,
            }, status=status.HTTP_401_UNAUTHORIZED)
        except ValidationError as exc:
            return Response({
                'message': 'Đăng nhập thất bại.',
                'errors': exc.detail,
            }, status=status.HTTP_400_BAD_REQUEST)

        tokens = serializer.validated_data
        user = serializer.user
        return Response({
            'message': 'Đăng nhập thành công.',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
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
    # khi sử dụng API này, người dùng phải được xác thực
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() # Đưa token vào blacklist
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
#============================
# profile view
#===========================
class ProfileView(APIView):
    # khi sử dụng API này, người dùng phải được xác thực
    permission_classes = (IsAuthenticated,)
    # Lấy thông tin profile của người dùng hiện tại
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

#============================
# change profile view
#============================
class ChangeProfileView(APIView):
    # khi sử dụng API này, người dùng phải được xác thực
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
    # khi sử dụng API này, người dùng phải được xác thực
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