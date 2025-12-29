import tempfile
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ai_engine.yolo_infer import predict_image

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