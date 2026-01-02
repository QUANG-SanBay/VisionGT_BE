from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
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

# def register_view(request):
#     return HttpResponse("This is the register view.")
# def logout_view(request):
#     return HttpResponse("This is the logout view.")