from django.conf import settings
from django.db import models
from traffic_signs.models import TrafficSign

# Create your models here.
class RecognitionHistory(models.Model):
    # id = models.CharField(max_length=100, primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    input_image_url = models.URLField(max_length=200)
    ouput_image_url = models.URLField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Recognition by {self.user.username} at {self.timestamp}"
class RecognitionResult(models.Model):

    bounding_box = models.JSONField()   # e.g., {"x": 10, "y": 20, "width": 100, "height": 50}
    confidence_score = models.FloatField()
    history = models.ForeignKey(RecognitionHistory, on_delete=models.CASCADE, related_name='results')
    traffic_sign = models.ForeignKey(TrafficSign, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.sign_name} ({self.confidence_score*100:.2f}%)"