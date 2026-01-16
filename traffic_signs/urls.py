from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrafficSignViewSet

router = DefaultRouter()
router.register(r'', TrafficSignViewSet, basename='traffic-signs')

urlpatterns = [
    path('', include(router.urls)),
]
