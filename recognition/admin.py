from django.contrib import admin
from .models import RecognitionHistory, RecognitionResult
# Register your models here.
admin.site.register(RecognitionHistory)
admin.site.register(RecognitionResult)
