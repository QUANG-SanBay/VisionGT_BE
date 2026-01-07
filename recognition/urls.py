from django.urls import path

from .views import (
	DetectionUploadRunView,
	DetectionDetailView,
	TrafficSignDetectView,
)


urlpatterns = [
	path("upload-run/", DetectionUploadRunView.as_view(), name="upload-run"),
	path("detection/<int:pk>/", DetectionDetailView.as_view(), name="detection-detail"),
	path("detect/", TrafficSignDetectView.as_view(), name="detect"),
]
