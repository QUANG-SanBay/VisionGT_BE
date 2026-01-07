import tempfile
from pathlib import Path
from django.core.files import File
from django.core.exceptions import FieldError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ai_engine.yolo_infer import predict_image, predict_image_with_save, predict_video_with_save
from .models import Detection, RecognitionHistory, RecognitionResult
from .serializers import DetectionUploadSerializer, DetectionSerializer, RecognitionHistorySerializer
from traffic_signs.models import TrafficSign


def _guess_file_type(file_name: str) -> str:
    suffix = Path(file_name).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        return "image"
    if suffix in {".mp4", ".mov", ".avi", ".mkv"}:
        return "video"
    return "unknown"


def _bbox_to_dict(bbox):
    try:
        x1, y1, x2, y2 = bbox
        return {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": x2 - x1,
            "height": y2 - y1,
        }
    except Exception:
        return {"bbox": bbox}


class DetectionUploadRunView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DetectionUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Upload failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = serializer.validated_data["file"]
        run_now = serializer.validated_data.get("run_now", True)
        file_type = _guess_file_type(file_obj.name)

        if file_type == "unknown":
            return Response({"message": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

        detection = Detection.objects.create(file=file_obj, file_type=file_type, status="pending")

        if not run_now:
            return Response(DetectionSerializer(detection, context={"request": request}).data, status=status.HTTP_201_CREATED)

        try:
            input_path = Path(detection.file.path)
            if file_type == "image":
                detections, out_path = predict_image_with_save(input_path)
            else:
                return Response({"message": "Video inference is not supported with remote model"}, status=status.HTTP_400_BAD_REQUEST)

            detection.result = {"detections": detections}
            detection.status = "done"
            if out_path and out_path.exists():
                detection.output_file.name = f"results/{out_path.name}"
            detection.save()

            history_data = self._save_history(request, detections, detection)
            return Response({
                "detection": DetectionSerializer(detection, context={"request": request}).data,
                "history": history_data,
            }, status=status.HTTP_200_OK)
        except Exception as exc:
            detection.status = "failed"
            detection.error_message = str(exc)
            detection.save(update_fields=["status", "error_message"])
            return Response({"message": "Inference failed", "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _match_sign(self, class_id):
        try:
            if hasattr(TrafficSign, "model_class_id"):
                return TrafficSign.objects.filter(model_class_id=class_id).first()
            return None
        except FieldError:
            return None
        except Exception:
            return None

    def _save_history(self, request, detections, detection: Detection):
        input_url = request.build_absolute_uri(detection.file.url) if detection.file else None
        output_url = request.build_absolute_uri(detection.output_file.url) if detection.output_file else None

        history = RecognitionHistory.objects.create(
            user=request.user,
            input_image_url=input_url,
            ouput_image_url=output_url,
        )

        for det in detections:
            sign = self._match_sign(det.get("class_id")) if det else None
            RecognitionResult.objects.create(
                bounding_box=_bbox_to_dict(det.get("bbox")) if det else {},
                confidence_score=det.get("confidence", 0) if det else 0,
                history=history,
                traffic_sign=sign,
            )

        return RecognitionHistorySerializer(history).data


class DetectionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            detection = Detection.objects.get(pk=pk)
        except Detection.DoesNotExist:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(DetectionSerializer(detection, context={"request": request}).data, status=status.HTTP_200_OK)


# View cũ demo nhanh ảnh đơn
class TrafficSignDetectView(APIView):
    def post(self, request):
        if "file" not in request.FILES:
            return Response({"detail": "Thiếu file ảnh"}, status=status.HTTP_400_BAD_REQUEST)
        uploaded = request.FILES["file"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
            for chunk in uploaded.chunks():
                tmp.write(chunk)
            tmp_path = Path(tmp.name)
        detections = predict_image(tmp_path)
        tmp_path.unlink(missing_ok=True)
        return Response({"detections": detections}, status=status.HTTP_200_OK)