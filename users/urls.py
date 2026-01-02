from django.urls import path
from . import views
urlpatterns = [
    # path('login/', views.login_view, name='login'),
    path('api/register/', views.registerAPI_view.as_view(), name='register'), 
    # path('logout/', views.logout_view, name='logout'),
]
