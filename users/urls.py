from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'manage', views.UserManagementViewSet, basename='user-management')

urlpatterns = [
    path('register/', views.registerAPI_view.as_view(), name='register'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('google/', views.GoogleLogin.as_view(), name='google_login'),
    path('facebook/', views.FacebookLogin.as_view(), name='facebook_login'),
    
    path ('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout_api'),
    
    path('profile/', views.ProfileView.as_view(), name='profile_api'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password_api'),
    path('change-profile/', views.ChangeProfileView.as_view(), name='change_profile_api'),
    
    # Admin user management routes
    path('', include(router.urls)),
]
