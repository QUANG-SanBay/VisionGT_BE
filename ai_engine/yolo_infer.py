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

# Import mapping từ class_id sang sign_code
from .sign_code_mapping import CLASS_ID_TO_SIGN_CODE
from .performance_config import (
    FRAME_STRIDE, BATCH_SIZE, INPUT_SIZE,
    FFMPEG_PRESET, FFMPEG_CRF
)


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "media" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


FONT_SIZE = 12  # tăng cỡ chữ cho video/ảnh
TEXT_COLOR = (255, 0, 0)          # đỏ
TEXT_BG_COLOR = (0, 0, 0, 160)    # nền đen trong suốt
YOLO_INPUT_SIZE = INPUT_SIZE  # Sử dụng giá trị từ performance_config


@lru_cache(maxsize=1)
def _load_local_model():
    weight_path = os.environ.get("YOLO_WEIGHTS") or config("YOLO_WEIGHTS", default=None)
    if not weight_path:
        weight_path = BASE_DIR / "ai_engine" / "YOLO11" / "best.pt"
    weight_path = Path(weight_path)
    if not weight_path.exists():
        raise FileNotFoundError(f"YOLO weight file not found: {weight_path}")
    return YOLO(str(weight_path))


def _run_yolo_on_image(image_path: Path, conf: float) -> Tuple[list, tuple]:
    """
    Chạy YOLO inference trên ảnh
    Returns: (detections, original_size)
    """
    # Đọc ảnh gốc
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    original_h, original_w = img.shape[:2]
    original_size = (original_w, original_h)
    
    # Resize về 640x640 để inference (như khi train model)
    img_resized = cv2.resize(img, (YOLO_INPUT_SIZE, YOLO_INPUT_SIZE))
    
    # Run YOLO inference
    model = _load_local_model()
    results = model.predict(source=img_resized, conf=conf, verbose=False)
    detections = _convert_results(results)
    
    # Scale bounding boxes về kích thước ảnh gốc
    scale_x = original_w / YOLO_INPUT_SIZE
    scale_y = original_h / YOLO_INPUT_SIZE
    
    for det in detections:
        bbox = det.get("bbox", [])
        if len(bbox) == 4:
            x1, y1, x2, y2 = bbox
            det["bbox"] = [
                x1 * scale_x,
                y1 * scale_y,
                x2 * scale_x,
                y2 * scale_y
            ]
    
    return detections, original_size


def _run_yolo_on_frame(frame, conf: float, original_size: tuple = None) -> list:
    """
    Chạy YOLO inference trên một frame video
    Args:
        frame: Frame gốc
        conf: Confidence threshold
        original_size: (width, height) của frame gốc, nếu None sẽ lấy từ frame
    """
    if original_size is None:
        original_h, original_w = frame.shape[:2]
        original_size = (original_w, original_h)
    else:
        original_w, original_h = original_size
    
    # Resize về 640x640 để inference
    frame_resized = cv2.resize(frame, (YOLO_INPUT_SIZE, YOLO_INPUT_SIZE))
    
    # Run YOLO inference
    model = _load_local_model()
    results = model.predict(source=frame_resized, conf=conf, verbose=False)
    detections = _convert_results(results)
    
    # Scale bounding boxes về kích thước gốc
    scale_x = original_w / YOLO_INPUT_SIZE
    scale_y = original_h / YOLO_INPUT_SIZE
    
    for det in detections:
        bbox = det.get("bbox", [])
        if len(bbox) == 4:
            x1, y1, x2, y2 = bbox
            det["bbox"] = [
                x1 * scale_x,
                y1 * scale_y,
                x2 * scale_x,
                y2 * scale_y
            ]
    
    return detections


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


def _get_sign_code_label(det: dict) -> str:
    """Lấy mã biển báo để hiển thị label"""
    class_id = det.get("class_id")
    if class_id is not None and class_id in CLASS_ID_TO_SIGN_CODE:
        return CLASS_ID_TO_SIGN_CODE[class_id]
    # Fallback về class_id nếu không tìm thấy mapping
    return str(class_id if class_id is not None else "")


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
        # Sử dụng mã biển báo thay vì tên
        label = _get_sign_code_label(det)
        _draw_label_with_bg(draw, (x1, max(0, y1 - FONT_SIZE)), label, font)
    run_name = f"img_{uuid.uuid4().hex}"
    out_path = OUTPUT_DIR / f"{run_name}.jpg"
    img.convert("RGB").save(out_path)
    return out_path


def predict_image(image_path: Path, conf: float = 0.25):
    detections, _ = _run_yolo_on_image(image_path, conf=conf)
    return detections


def predict_image_with_save(image_path: Path, conf: float = 0.25) -> Tuple[list, Path]:
    detections, _ = _run_yolo_on_image(image_path, conf=conf)
    out_path = _draw_and_save(image_path, detections)
    return detections, out_path


def _run_yolo_batch(model, frames_batch: list, conf: float, original_size: tuple) -> list:
    """Xử lý batch của frames"""
    results = model.predict(source=frames_batch, conf=conf, verbose=False, stream=False)
    
    original_w, original_h = original_size
    scale_x = original_w / YOLO_INPUT_SIZE
    scale_y = original_h / YOLO_INPUT_SIZE
    
    all_detections = []
    for res in results:
        detections = _convert_results([res])
        # Scale bounding boxes về kích thước gốc
        for det in detections:
            bbox = det.get("bbox", [])
            if len(bbox) == 4:
                x1, y1, x2, y2 = bbox
                det["bbox"] = [
                    x1 * scale_x,
                    y1 * scale_y,
                    x2 * scale_x,
                    y2 * scale_y
                ]
        all_detections.append(detections)
    
    return all_detections


def predict_video_with_save(video_path: Path, conf: float = 0.25) -> Tuple[list, Path, float]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames_orig = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames_orig / fps if fps > 0 else 0

    temp_path = OUTPUT_DIR / f"temp_{uuid.uuid4().hex}.mp4"
    out_path = OUTPUT_DIR / f"vid_{uuid.uuid4().hex}.mp4"
    
    # Cấu hình xử lý: chỉ detect ~7 frame/giây để tăng tốc
    TARGET_DETECTION_FPS = 7.0
    frame_stride = max(1, int(fps / TARGET_DETECTION_FPS))  # Tính frame_stride dựa trên FPS gốc
    
    # Tính số frame thực tế sẽ detect
    num_detected_frames = (total_frames_orig + frame_stride - 1) // frame_stride
    
    # Tính output_fps để giữ đúng thời lượng video gốc
    output_fps = num_detected_frames / duration if duration > 0 else TARGET_DETECTION_FPS
    
    print(f"📹 Video gốc: {fps:.1f}fps, {duration:.1f}s, {total_frames_orig} frames")
    print(f"📹 Detection: stride={frame_stride}, ~{num_detected_frames} frames")
    print(f"📹 Output: {output_fps:.2f}fps để giữ thời lượng {duration:.1f}s")
    
    # Sử dụng mp4v codec với output_fps đã tính
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_path), fourcc, output_fps, (width, height))
    
    if not writer.isOpened():
        raise RuntimeError("Cannot initialize video writer. Please check OpenCV installation.")

    results = []
    frame_idx = 0
    batch_size = BATCH_SIZE
    
    # Lưu kích thước gốc để scale bounding boxes
    original_size = (width, height)
    
    # Batch processing
    model = _load_local_model()
    frames_batch = []
    frames_data = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # Xử lý batch cuối cùng nếu còn
                if frames_batch:
                    detections_batch = _run_yolo_batch(model, frames_batch, conf, original_size)
                    for i, (frame_to_write, idx) in enumerate(frames_data):
                        _draw_boxes_on_frame(frame_to_write, detections_batch[i])
                        writer.write(frame_to_write)
                        results.append({"frame_index": idx, "detections": detections_batch[i]})
                break

            if frame_idx % frame_stride == 0:
                # Resize frame cho inference
                frame_resized = cv2.resize(frame, (YOLO_INPUT_SIZE, YOLO_INPUT_SIZE))
                frames_batch.append(frame_resized)
                frames_data.append((frame.copy(), frame_idx))
                
                # Khi đủ batch_size thì xử lý
                if len(frames_batch) >= batch_size:
                    detections_batch = _run_yolo_batch(model, frames_batch, conf, original_size)
                    for i, (frame_to_write, idx) in enumerate(frames_data):
                        _draw_boxes_on_frame(frame_to_write, detections_batch[i])
                        writer.write(frame_to_write)  # Chỉ ghi frame đã detect
                        results.append({"frame_index": idx, "detections": detections_batch[i]})
                    frames_batch = []
                    frames_data = []
            # Bỏ qua frame không detect - KHÔNG ghi vào video output
                
            frame_idx += 1
    finally:
        cap.release()
        writer.release()
    
    # Convert video sang H.264 để tương thích với web browsers
    try:
        import subprocess
        print(f"🔄 Converting video to H.264 for web compatibility...")
        
        # Thử convert bằng ffmpeg
        result = subprocess.run([
            'ffmpeg', '-i', str(temp_path),
            '-c:v', 'libx264',  # H.264 codec
            '-preset', FFMPEG_PRESET,  # Sử dụng giá trị từ performance_config
            '-crf', str(FFMPEG_CRF),  # Sử dụng giá trị từ performance_config
            '-pix_fmt', 'yuv420p',  # Pixel format cho web compatibility
            '-movflags', '+faststart',  # Enable streaming
            '-y',  # Overwrite output
            str(out_path)
        ], capture_output=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Video converted to H.264 successfully")
            # Xóa file temp
            temp_path.unlink(missing_ok=True)
        else:
            print(f"⚠️  FFmpeg conversion failed, using original video")
            # Rename temp file thành out file
            temp_path.rename(out_path)
    except (FileNotFoundError, subprocess.SubprocessError) as e:
        print(f"⚠️  FFmpeg not found or conversion failed: {e}")
        print(f"   Using mp4v codec (may not play in all browsers)")
        # Rename temp file thành out file
        temp_path.rename(out_path)

    # Trả về output_fps đã tính toán để giữ đúng thời lượng
    return results, out_path, float(output_fps)


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
        # Sử dụng mã biển báo thay vì tên
        label = _get_sign_code_label(det)
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