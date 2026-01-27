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
    IMAGE_INPUT_SIZE, IMAGE_CONF_THRESHOLD,
    VIDEO_BATCH_SIZE, VIDEO_INPUT_SIZE, VIDEO_CONF_THRESHOLD,
    VIDEO_TARGET_DETECTION_FPS,
    FFMPEG_PRESET, FFMPEG_CRF
)


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "media" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


FONT_SIZE = 12  # tăng cỡ chữ cho video/ảnh
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
    
    print("🔥 Loading YOLO model...")
    model = YOLO(str(weight_path))
    
    # Warm-up model với dummy inference để tăng tốc cho lần đầu
    print("⚡ Warming up model...")
    try:
        dummy_img = np.zeros((IMAGE_INPUT_SIZE, IMAGE_INPUT_SIZE, 3), dtype=np.uint8)
        model.predict(source=dummy_img, conf=0.5, verbose=False)
        print("✅ Model warmed up successfully")
    except Exception as e:
        print(f"⚠️  Model warm-up failed (non-critical): {e}")
    
    return model


def _run_yolo_on_image(image_path: Path, conf: float) -> Tuple[list, tuple]:
    """
    Chạy YOLO inference trên ảnh với độ chính xác cao nhất
    Returns: (detections, original_size)
    """
    print(f"🖼️  Processing image with high accuracy settings...")
    print(f"   Input size: {IMAGE_INPUT_SIZE}x{IMAGE_INPUT_SIZE}, Confidence: {conf}")
    
    # Đọc ảnh gốc
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    original_h, original_w = img.shape[:2]
    original_size = (original_w, original_h)
    
    # Resize về IMAGE_INPUT_SIZE để inference (độ chính xác cao)
    img_resized = cv2.resize(img, (IMAGE_INPUT_SIZE, IMAGE_INPUT_SIZE))
    
    # Run YOLO inference với settings tối ưu cho ảnh
    model = _load_local_model()
    results = model.predict(
        source=img_resized, 
        conf=conf, 
        verbose=False,
        iou=0.5,  # IoU threshold cho NMS
        max_det=100  # Tăng số detection tối đa
    )
    detections = _convert_results(results)
    
    print(f"   ✅ Detected {len(detections)} signs")
    
    # Scale bounding boxes về kích thước ảnh gốc
    scale_x = original_w / IMAGE_INPUT_SIZE
    scale_y = original_h / IMAGE_INPUT_SIZE
    
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


def predict_image(image_path: Path, conf: float = None):
    """Predict trên ảnh với confidence mặc định cho độ chính xác cao"""
    if conf is None:
        conf = IMAGE_CONF_THRESHOLD
    detections, _ = _run_yolo_on_image(image_path, conf=conf)
    return detections


def predict_image_with_save(image_path: Path, conf: float = None) -> Tuple[list, Path]:
    """Predict và save ảnh với độ chính xác cao nhất"""
    if conf is None:
        conf = IMAGE_CONF_THRESHOLD
    detections, _ = _run_yolo_on_image(image_path, conf=conf)
    out_path = _draw_and_save(image_path, detections)
    return detections, out_path


def _run_yolo_batch(model, frames_batch: list, conf: float, original_size: tuple) -> list:
    """Xử lý batch của frames cho video"""
    results = model.predict(
        source=frames_batch, 
        conf=conf, 
        verbose=False, 
        stream=False,
        iou=0.6  # IoU cao hơn cho video
    )
    
    original_w, original_h = original_size
    scale_x = original_w / VIDEO_INPUT_SIZE
    scale_y = original_h / VIDEO_INPUT_SIZE
    
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


def predict_video_with_save(video_path: Path, conf: float = None) -> Tuple[list, Path, float]:
    """Xử lý video với cấu hình tối ưu riêng"""
    if conf is None:
        conf = VIDEO_CONF_THRESHOLD
    
    print(f"🎬 Processing video with optimized settings...")
    print(f"   Input size: {VIDEO_INPUT_SIZE}x{VIDEO_INPUT_SIZE}, Confidence: {conf}")
    print(f"   Target detection FPS: {VIDEO_TARGET_DETECTION_FPS}")
    
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
    
    # Sử dụng config từ performance_config
    frame_stride = max(1, int(fps / VIDEO_TARGET_DETECTION_FPS))  # Tính frame_stride dựa trên FPS gốc
    
    print(f"📹 Video gốc: {fps:.1f}fps, {duration:.1f}s, {total_frames_orig} frames")
    print(f"📹 Detection: stride={frame_stride}, chỉ detect mỗi {frame_stride} frame")
    print(f"📹 Output: {fps:.1f}fps (giữ FPS gốc), ghi TẤT CẢ frames")
    
    # GHI VIDEO VỚI FPS GỐC để giữ đúng thời lượng
    # Chỉ detect trên một số frames nhưng GHI TẤT CẢ frames
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_path), fourcc, fps, (width, height))
    
    if not writer.isOpened():
        raise RuntimeError("Cannot initialize video writer. Please check OpenCV installation.")

    results = []
    frame_idx = 0
    batch_size = VIDEO_BATCH_SIZE  # Sử dụng config riêng cho video
    
    # Lưu kích thước gốc để scale bounding boxes
    original_size = (width, height)
    
    # Batch processing
    model = _load_local_model()
    frames_batch = []
    frames_data = []

    # Cache detections cho các frames đã detect
    frame_detections_map = {}  # {frame_idx: detections}
    
    try:
        # PASS 1: Detect trên các frames theo stride
        print(f"🔍 Pass 1: Detection...")
        while True:
            ret, frame = cap.read()
            if not ret:
                # Xử lý batch cuối cùng nếu còn
                if frames_batch:
                    detections_batch = _run_yolo_batch(model, frames_batch, conf, original_size)
                    for i, (_, idx) in enumerate(frames_data):
                        frame_detections_map[idx] = detections_batch[i]
                        results.append({"frame_index": idx, "detections": detections_batch[i]})
                break

            if frame_idx % frame_stride == 0:
                # Resize frame cho inference với VIDEO_INPUT_SIZE
                frame_resized = cv2.resize(frame, (VIDEO_INPUT_SIZE, VIDEO_INPUT_SIZE))
                frames_batch.append(frame_resized)
                frames_data.append((None, frame_idx))  # Không cần lưu frame gốc
                
                # Khi đủ batch_size thì xử lý
                if len(frames_batch) >= batch_size:
                    detections_batch = _run_yolo_batch(model, frames_batch, conf, original_size)
                    for i, (_, idx) in enumerate(frames_data):
                        frame_detections_map[idx] = detections_batch[i]
                        results.append({"frame_index": idx, "detections": detections_batch[i]})
                    frames_batch = []
                    frames_data = []
                
            frame_idx += 1
        
        # PASS 2: Ghi TẤT CẢ frames với detections từ frame gần nhất
        print(f"✍️  Pass 2: Writing all frames with detections...")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset về đầu video
        frame_idx = 0
        last_detections = []  # Cache detection gần nhất
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Nếu frame này có detections thì dùng, không thì dùng detections gần nhất
            if frame_idx in frame_detections_map:
                last_detections = frame_detections_map[frame_idx]
            
            # Vẽ detections lên frame
            if last_detections:
                _draw_boxes_on_frame(frame, last_detections)
            
            # GHI TẤT CẢ frames
            writer.write(frame)
            frame_idx += 1
    finally:
        cap.release()
        writer.release()
    
    # Convert video sang H.264 để tương thích với web browsers
    try:
        import subprocess
        print(f"🔄 Converting video to H.264 for web compatibility...")
        
        # FFmpeg với các flags tối ưu cho web streaming
        result = subprocess.run([
            'ffmpeg', '-i', str(temp_path),
            '-c:v', 'libx264',  # H.264 codec
            '-preset', FFMPEG_PRESET,
            '-crf', str(FFMPEG_CRF),
            '-pix_fmt', 'yuv420p',  # Pixel format cho web compatibility
            '-movflags', '+faststart',  # Enable progressive streaming
            '-r', str(fps),  # Force output FPS = input FPS
            '-vsync', 'cfr',  # Constant frame rate
            '-g', str(int(fps * 2)),  # Keyframe interval (2 giây)
            '-sc_threshold', '0',  # Disable scene change detection
            '-force_key_frames', f'expr:gte(t,n_forced*2)',  # Force keyframe mỗi 2s
            '-t', str(duration),  # CRITICAL: Set exact duration
            '-y',
            str(out_path)
        ], capture_output=True, timeout=300, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print(f"✅ Video converted to H.264 successfully")
            temp_path.unlink(missing_ok=True)
        else:
            print(f"⚠️  FFmpeg conversion failed: {result.stderr}")
            temp_path.rename(out_path)
    except (FileNotFoundError, subprocess.SubprocessError) as e:
        print(f"⚠️  FFmpeg not found or conversion failed: {e}")
        temp_path.rename(out_path)

    # Trả về FPS GỐC để tính thời gian xuất hiện ĐÚNG
    # output_fps chỉ dùng để ghi video, không dùng để tính thời gian!
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