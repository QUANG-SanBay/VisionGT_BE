# Performance configuration cho YOLO inference

# Frame stride: skip frames để xử lý nhanh hơn
# 1 = xử lý mọi frame, 3 = xử lý mỗi 3 frame
FRAME_STRIDE = 1

# Batch size cho video processing
BATCH_SIZE = 4

# YOLO input size (nhỏ hơn = nhanh hơn nhưng độ chính xác thấp hơn)
# Options: 320, 416, 640
INPUT_SIZE = 640

# FFmpeg preset cho video encoding
# Options: 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium'
FFMPEG_PRESET = 'ultrafast'

# CRF (Constant Rate Factor) cho video quality
# 18-28 recommended, cao hơn = file nhỏ hơn nhưng chất lượng thấp hơn
FFMPEG_CRF = 28
