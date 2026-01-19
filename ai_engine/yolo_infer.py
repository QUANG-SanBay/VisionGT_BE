import os
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Tuple

import cv2
from decouple import config
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "media" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


FONT_SIZE = 20  # tăng cỡ chữ cho video/ảnh
TEXT_COLOR = (255, 0, 0)          # đỏ
TEXT_BG_COLOR = (0, 0, 0, 160)    # nền đen trong suốt


@lru_cache(maxsize=1)
def _load_local_model():
    weight_path = os.environ.get("YOLO_WEIGHTS") or config("YOLO_WEIGHTS", default=None)
    if not weight_path:
        weight_path = BASE_DIR / "ai_engine" / "YOLO11" / "best.pt"
    weight_path = Path(weight_path)
    if not weight_path.exists():
        raise FileNotFoundError(f"YOLO weight file not found: {weight_path}")
    return YOLO(str(weight_path))


def _run_yolo_on_image(image_path: Path, conf: float) -> list:
    model = _load_local_model()
    results = model.predict(source=str(image_path), conf=conf, verbose=False)
    return _convert_results(results)


def _run_yolo_on_frame(frame, conf: float) -> list:
    model = _load_local_model()
    results = model.predict(source=frame, conf=conf, verbose=False)
    return _convert_results(results)


def _convert_results(results) -> list:
    detections = []
    if not results:
        return detections
    res = results[0]
    names = res.names or {}
    for box in res.boxes:
        cls_id = int(box.cls.item()) if box.cls is not None else None
        conf_score = float(box.conf.item()) if box.conf is not None else 0.0
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        detections.append({
            "class_id": cls_id,
            "class_name": names.get(cls_id, str(cls_id)),
            "confidence": conf_score,
            "bbox": [float(x1), float(y1), float(x2), float(y2)],
        })
    return detections


def _draw_and_save(image_path: Path, detections: list) -> Path:
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = _get_font()
    for det in detections:
        bbox = det.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        x1, y1, x2, y2 = bbox
        draw.rectangle([x1, y1, x2, y2], outline=TEXT_COLOR, width=2)
        label = str(det.get("class_name") or det.get("class_id", ""))
        _draw_label_with_bg(draw, (x1, max(0, y1 - FONT_SIZE)), label, font)
    run_name = f"img_{uuid.uuid4().hex}"
    out_path = OUTPUT_DIR / f"{run_name}.jpg"
    img.convert("RGB").save(out_path)
    return out_path


def predict_image(image_path: Path, conf: float = 0.25):
    return _run_yolo_on_image(image_path, conf=conf)


def predict_image_with_save(image_path: Path, conf: float = 0.25) -> Tuple[list, Path]:
    detections = _run_yolo_on_image(image_path, conf=conf)
    out_path = _draw_and_save(image_path, detections)
    return detections, out_path


def predict_video_with_save(video_path: Path, conf: float = 0.25) -> Tuple[list, Path, float]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out_path = OUTPUT_DIR / f"vid_{uuid.uuid4().hex}.mp4"
    
    # Sử dụng H.264 codec để tương thích với web browsers
    # Thử các codec theo thứ tự ưu tiên
    codecs_to_try = [
        ('avc1', 'H.264 - tốt nhất cho web'),
        ('H264', 'H.264 alternative'),
        ('X264', 'x264 encoder'),
        ('mp4v', 'MPEG-4 fallback')
    ]
    
    writer = None
    for codec, desc in codecs_to_try:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            test_writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))
            if test_writer.isOpened():
                writer = test_writer
                print(f"✅ Using codec: {codec} ({desc})")
                break
            else:
                test_writer.release()
        except Exception as e:
            print(f"⚠️  Codec {codec} failed: {e}")
            continue
    
    if writer is None:
        raise RuntimeError("Cannot initialize video writer with any codec. Please install ffmpeg or codec pack.")


    results = []
    frame_idx = 0
    frame_stride = 1  # adjust >1 to sample fewer frames if needed

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = []
            if frame_idx % frame_stride == 0:
                detections = _run_yolo_on_frame(frame, conf=conf)

            _draw_boxes_on_frame(frame, detections)
            writer.write(frame)
            results.append({"frame_index": frame_idx, "detections": detections})
            frame_idx += 1
    finally:
        cap.release()
        writer.release()

    return results, out_path, float(fps)


def _draw_boxes_on_frame(frame, detections: list):
    font = _get_font()
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    draw = ImageDraw.Draw(img)
    for det in detections:
        bbox = det.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        x1, y1, x2, y2 = map(int, bbox)
        draw.rectangle([x1, y1, x2, y2], outline=TEXT_COLOR, width=2)
        label = str(det.get("class_name") or det.get("class_id", ""))
        _draw_label_with_bg(draw, (x1, max(0, y1 - FONT_SIZE)), label, font)
    frame[:] = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


@lru_cache(maxsize=1)
def _get_font(size: int = FONT_SIZE):
    try:
        local_font = BASE_DIR / "ai_engine" / "fonts" / "DejaVuSans.ttf"
        if local_font.exists():
            return ImageFont.truetype(str(local_font), size=size)
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def _draw_label_with_bg(draw: ImageDraw.ImageDraw, xy: tuple, text: str, font: ImageFont.ImageFont):
    if not text:
        return
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    if not bbox:
        return
    x0, y0, x1, y1 = bbox
    padding = 4
    draw.rectangle([x0 - padding, y0 - padding, x1 + padding, y1 + padding], fill=TEXT_BG_COLOR)
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)