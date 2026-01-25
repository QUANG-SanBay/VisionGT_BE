# Performance configuration cho YOLO inference

# ============================================
# IMAGE PROCESSING (Độ chính xác tối đa)
# ============================================
IMAGE_INPUT_SIZE = 320  # Giữ nguyên kích thước cao nhất cho độ chính xác
IMAGE_CONF_THRESHOLD = 0.5  # Confidence thấp hơn để detect nhiều hơn

# ============================================
# VIDEO PROCESSING (Cân bằng tốc độ & độ chính xác)
# ============================================
# Batch size cho video processing
VIDEO_BATCH_SIZE = 4

# YOLO input size cho video (có thể giảm để tăng tốc)
# Options: 320, 416, 640
VIDEO_INPUT_SIZE = 320  # Giữ 640 để đảm bảo độ chính xác

# Confidence threshold cho video (cao hơn để giảm false positive)
VIDEO_CONF_THRESHOLD = 0.5

# Target FPS cho detection (giảm để xử lý nhanh hơn)
VIDEO_TARGET_DETECTION_FPS = 7.0

# ============================================
# VIDEO ENCODING
# ============================================
# FFmpeg preset cho video encoding
# Options: 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium'
FFMPEG_PRESET = 'ultrafast'

# CRF (Constant Rate Factor) cho video quality
# 18-28 recommended, cao hơn = file nhỏ hơn nhưng chất lượng thấp hơn
FFMPEG_CRF = 28
