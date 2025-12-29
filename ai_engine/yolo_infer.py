from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHT_PATH = BASE_DIR / "ai_engine" / "weights" / "yolov8m_final.pt"
_model = YOLO(str(WEIGHT_PATH))  # tải một lần khi import

def predict_image(image_path: Path, conf: float = 0.25):
    # Trả về list các detection dạng dict
    results = _model.predict(source=str(image_path), imgsz=640, conf=conf, device="cpu")
    detections = []
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf_score = float(box.conf[0])
        x1, y1, x2, y2 = map(float, box.xyxy[0])
        detections.append({
            "class_id": cls_id,
            "confidence": conf_score,
            "bbox": [x1, y1, x2, y2],
        })
    return detections