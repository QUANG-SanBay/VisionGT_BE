from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer

# Create your views here.
class registerAPI_view(APIView):
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Đăng nhập với JWT 
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
    
#logout view
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() # Đưa token vào blacklist
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# View đăng nhập sử dụng serializer thông thường
# class loginAPI_view(APIView):
#     def post(self, request):
#         serializer = loginSerializer(data=request.data)
#         if serializer.is_valid():
#             # Xử lý đăng nhập ở đây (ví dụ: xác thực người dùng)
#             user = serializer.submit()
#             message = {
#                 'message': 'Login successful.',
#                 'user': {
#                     'email': user.email,
#                     'full_name': user.get_full_name(),
#                 }
#             }
#             return Response(message, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# def logout_view(request):
#     return HttpResponse("This is the logout view.")