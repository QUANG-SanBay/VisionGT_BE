from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
urlpatterns = [
    path('api/register/', views.registerAPI_view.as_view(), name='register'),
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path ('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', views.LogoutView.as_view(), name='logout_api'),
    
    path('api/profile/', views.ProfileView.as_view(), name='profile_api'),
]
