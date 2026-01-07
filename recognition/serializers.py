from django.conf import settings
from rest_framework import serializers
from .models import Detection, RecognitionHistory, RecognitionResult
from traffic_signs.models import TrafficSign


class DetectionUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    run_now = serializers.BooleanField(required=False, default=True)


class DetectionSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    output_url = serializers.SerializerMethodField()

    class Meta:
        model = Detection
        fields = [
            "id",
            "file_type",
            "status",
            "result",
            "error_message",
            "file_url",
            "output_url",
            "created_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if obj.file and request else (obj.file.url if obj.file else None)

    def get_output_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.output_file.url) if obj.output_file and request else (obj.output_file.url if obj.output_file else None)


class TrafficSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficSign
        fields = [
            "sign_Code",
            "name",
            "description",
            "category",
            "image_url",
            "penalty_details",
        ]


class RecognitionResultSerializer(serializers.ModelSerializer):
    traffic_sign = TrafficSignSerializer(read_only=True)

    class Meta:
        model = RecognitionResult
        fields = [
            "id",
            "bounding_box",
            "confidence_score",
            "traffic_sign",
        ]


class RecognitionHistorySerializer(serializers.ModelSerializer):
    results = RecognitionResultSerializer(many=True, read_only=True)

    class Meta:
        model = RecognitionHistory
        fields = [
            "id",
            "timestamp",
            "input_image_url",
            "ouput_image_url",
            "results",
        ]
