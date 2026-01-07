import os
import uuid
from pathlib import Path
from typing import Tuple

from decouple import config
from PIL import Image, ImageDraw

try:
    from inference_sdk import InferenceHTTPClient
except Exception:
    InferenceHTTPClient = None


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "media" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _get_rf_client():
    api_key = os.environ.get("ROBOFLOW_API_KEY") or config("ROBOFLOW_API_KEY", default=None)
    if not api_key or InferenceHTTPClient is None:
        return None
    return InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key=api_key,
    )


def predict_image_remote(image_path: Path, model_id: str = None, conf: float = 0.25):
    client = _get_rf_client()
    if not client:
        raise RuntimeError("Roboflow client not configured. Set ROBOFLOW_API_KEY.")
    model_id = model_id or os.environ.get("ROBOFLOW_MODEL_ID") or config("ROBOFLOW_MODEL_ID", default="vietnam-traffic-sign-altsi-ofqyc/1")
    result = client.infer(str(image_path), model_id=model_id)
    detections = []
    for p in result.get("predictions", []):
        x, y, w, h = p["x"], p["y"], p["width"], p["height"]
        x1, y1 = x - w / 2, y - h / 2
        x2, y2 = x + w / 2, y + h / 2
        cls_id = p.get("class_id", p.get("class", None))
        conf_score = float(p.get("confidence", 0))
        if conf_score < conf:
            continue
        detections.append({
            "class_id": cls_id,
            "confidence": conf_score,
            "bbox": [float(x1), float(y1), float(x2), float(y2)],
        })
    return detections


def _draw_and_save(image_path: Path, detections: list) -> Path:
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    for det in detections:
        bbox = det.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        x1, y1, x2, y2 = bbox
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        label = str(det.get("class_id", ""))
        draw.text((x1, y1), label, fill="red")
    run_name = f"img_{uuid.uuid4().hex}"
    out_path = OUTPUT_DIR / f"{run_name}.jpg"
    img.save(out_path)
    return out_path


def predict_image(image_path: Path, conf: float = 0.25):
    return predict_image_remote(image_path, conf=conf)


def predict_image_with_save(image_path: Path, conf: float = 0.25) -> Tuple[list, Path]:
    detections = predict_image_remote(image_path, conf=conf)
    out_path = _draw_and_save(image_path, detections)
    return detections, out_path


def predict_video_with_save(video_path: Path, conf: float = 0.25) -> Tuple[list, Path]:
    raise RuntimeError("Video inference not supported with remote model")