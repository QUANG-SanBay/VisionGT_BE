from django.urls import path

from .views import (
    DetectionUploadRunView,
    DetectionDetailView,
    RecognitionHistoryListView,
)


urlpatterns = [
    path("upload-run/", DetectionUploadRunView.as_view(), name="upload-run"),
    path("detection/<int:pk>/", DetectionDetailView.as_view(), name="detection-detail"),
    path("history/", RecognitionHistoryListView.as_view(), name="history-list"),
]
