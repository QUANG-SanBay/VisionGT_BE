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
        ("done", "Done"),
        ("failed", "Failed"),
    )

    file = models.FileField(upload_to="uploads/")
    output_file = models.FileField(upload_to="results/", null=True, blank=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    status = models.CharField(max_length=10, choices=STATUSES, default="pending")
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detection {self.id} ({self.file_type})"


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