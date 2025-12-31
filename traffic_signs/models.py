from django.db import models

# Create your models here.
class TrafficSign(models.Model):
    sign_Code = models.CharField(max_length=10, primary_key= True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50)
    image_url = models.URLField(max_length=200, null=True, blank=True)
    penalty_details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}"
    