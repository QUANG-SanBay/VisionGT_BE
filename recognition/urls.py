from django.urls import path, re_path

from .views import (
    DetectionUploadRunView,
    DetectionDetailView,
    RecognitionHistoryListView,
    ServeMediaFileView,
)


urlpatterns = [
    path("upload-run/", DetectionUploadRunView.as_view(), name="upload-run"),
    path("detection/<int:pk>/", DetectionDetailView.as_view(), name="detection-detail"),
    path("history/", RecognitionHistoryListView.as_view(), name="history-list"),
    
    # Serve media files với proper headers cho video streaming
    re_path(r'^media/(?P<file_path>.+)$', ServeMediaFileView.as_view(), name='serve-media'),
]
