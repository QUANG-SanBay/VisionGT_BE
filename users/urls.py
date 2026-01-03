from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
urlpatterns = [
    # path('login/', views.login_view, name='login'),
    path('api/register/', views.registerAPI_view.as_view(), name='register'),
    # path('api/login/', views.loginAPI_view.as_view(), name='login'), 
    
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path ('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', views.LogoutView.as_view(), name='logout_api'),
    # path('logout/', views.logout_view, name='logout'),
]
