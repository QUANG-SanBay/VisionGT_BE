from django.conf import settings
from django.db import models
from traffic_signs.models import TrafficSign


class Detection(models.Model):
    FILE_TYPES = (
        ("image", "Image"),
        ("video", "Video"),
    )
    STATUSES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("done", "Done"),
        ("failed", "Failed"),
    )

    file = models.FileField(upload_to="uploads/")
    output_file = models.FileField(upload_to="results/", null=True, blank=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    status = models.CharField(max_length=15, choices=STATUSES, default="pending")
    fps = models.FloatField(null=True, blank=True)  # FPS cho video
    duration = models.FloatField(null=True, blank=True)  # Độ dài video (seconds)
    total_frames = models.IntegerField(null=True, blank=True)  # Tổng số frames
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Detection {self.id} ({self.file_type})"


class DetectedSign(models.Model):
    """Lưu thông tin chi tiết về từng biển báo được phát hiện"""
    detection = models.ForeignKey(Detection, on_delete=models.CASCADE, related_name="detected_signs")
    traffic_sign = models.ForeignKey(TrafficSign, on_delete=models.SET_NULL, null=True, blank=True)
    class_id = models.IntegerField()  # ID class từ YOLO model
    class_name = models.CharField(max_length=255)  # Tên biển báo từ YOLO
    confidence = models.FloatField()  # Độ tin cậy
    bbox = models.JSONField()  # Bounding box [x1, y1, x2, y2]
    
    # Thông tin thời gian cho video
    start_time = models.FloatField(null=True, blank=True)  # Thời gian bắt đầu xuất hiện (giây)
    end_time = models.FloatField(null=True, blank=True)  # Thời gian kết thúc xuất hiện (giây)
    frame_index = models.IntegerField(null=True, blank=True)  # Frame index nếu là ảnh hoặc một frame cụ thể
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time', 'frame_index']
        indexes = [
            models.Index(fields=['detection', 'start_time']),
            models.Index(fields=['traffic_sign']),
        ]

    def __str__(self):
        return f"{self.class_name} ({self.confidence:.2f}) - Detection {self.detection_id}"


class RecognitionHistory(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    input_image_url = models.URLField(max_length=200, null=True, blank=True)
    ouput_image_url = models.URLField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Recognition by {self.user.username} at {self.timestamp}"


class RecognitionResult(models.Model):
    bounding_box = models.JSONField()
    confidence_score = models.FloatField()
    history = models.ForeignKey(RecognitionHistory, on_delete=models.CASCADE, related_name="results")
    traffic_sign = models.ForeignKey(TrafficSign, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Result {self.id} ({self.confidence_score*100:.1f}%)"