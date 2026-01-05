from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
urlpatterns = [
    path('register/', views.registerAPI_view.as_view(), name='register'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path ('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout_api'),
    
    path('profile/', views.ProfileView.as_view(), name='profile_api'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password_api'),
    path('change-profile/', views.ChangeProfileView.as_view(), name='change_profile_api'),
]
