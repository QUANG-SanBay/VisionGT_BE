# API Nhận Diện Biển Báo Giao Thông - Hướng Dẫn Sử Dụng

## Tổng quan
API này sử dụng YOLO 11 model để nhận diện biển báo giao thông từ hình ảnh hoặc video. Khi upload file, API sẽ:
- Phát hiện các biển báo giao thông trong file
- Trả về thông tin chi tiết về từng biển báo
- Với video: theo dõi timeline xuất hiện của biển báo (từ giây nào đến giây nào)
- Link thông tin biển báo với database TrafficSign để lấy thông tin chi tiết (mô tả, hình phạt, v.v.)

## Endpoints

### 1. Upload và Nhận Diện File (Image/Video)

**Endpoint:** `POST /api/recognition/upload-run/`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): File hình ảnh hoặc video cần nhận diện
  - Image formats: `.jpg`, `.jpeg`, `.png`, `.bmp`
  - Video formats: `.mp4`, `.avi`, `.mov`, `.mkv`
- `file_type` (required): Loại file - `"image"` hoặc `"video"`

**Example Request (Python):**
```python
import requests

url = "http://localhost:8000/api/recognition/upload-run/"

# Upload ảnh
with open('traffic_sign.jpg', 'rb') as f:
    files = {'file': f}
    data = {'file_type': 'image'}
    response = requests.post(url, files=files, data=data)
    print(response.json())

# Upload video
with open('traffic_video.mp4', 'rb') as f:
    files = {'file': f}
    data = {'file_type': 'video'}
    response = requests.post(url, files=files, data=data)
    print(response.json())
```

**Example Request (cURL):**
```bash
# Upload ảnh
curl -X POST http://localhost:8000/api/recognition/upload-run/ \
  -F "file=@traffic_sign.jpg" \
  -F "file_type=image"

# Upload video
curl -X POST http://localhost:8000/api/recognition/upload-run/ \
  -F "file=@traffic_video.mp4" \
  -F "file_type=video"
```

**Example Response (Image):**
```json
{
    "success": true,
    "message": "Nhận diện thành công",
    "detection_id": 1,
    "file_type": "image",
    "data": {
        "id": 1,
        "file": "/media/uploads/traffic_sign.jpg",
        "output_file": "/media/results/img_abc123.jpg",
        "output_file_url": "http://localhost:8000/media/results/img_abc123.jpg",
        "file_type": "image",
        "status": "done",
        "fps": null,
        "duration": null,
        "total_frames": null,
        "error_message": null,
        "created_at": "2026-01-11T10:30:00Z",
        "detected_signs": [
            {
                "id": 1,
                "class_id": 2,
                "class_name": "Cấm đi ngược chiều",
                "confidence": 0.95,
                "bbox": [120.5, 80.3, 250.7, 200.9],
                "start_time": null,
                "end_time": null,
                "frame_index": 0,
                "traffic_sign": {
                    "sign_Code": "P.123",
                    "name": "Cấm đi ngược chiều",
                    "description": "Biển báo cấm các phương tiện đi ngược chiều...",
                    "category": "Biển cấm",
                    "image_url": "https://example.com/sign.jpg",
                    "penalty_details": "Phạt 4-6 triệu đồng, tước GPLX 1-3 tháng",
                    "model_class_id": "2"
                }
            }
        ]
    }
}
```

**Example Response (Video):**
```json
{
    "success": true,
    "message": "Nhận diện thành công",
    "detection_id": 2,
    "file_type": "video",
    "data": {
        "id": 2,
        "file": "/media/uploads/traffic_video.mp4",
        "output_file": "/media/results/vid_xyz789.mp4",
        "output_file_url": "http://localhost:8000/media/results/vid_xyz789.mp4",
        "file_type": "video",
        "status": "done",
        "fps": 30.0,
        "duration": 10.5,
        "total_frames": 315,
        "error_message": null,
        "created_at": "2026-01-11T10:35:00Z",
        "detected_signs": [
            {
                "id": 2,
                "class_id": 2,
                "class_name": "Cấm đi ngược chiều",
                "confidence": 0.93,
                "bbox": [120.5, 80.3, 250.7, 200.9],
                "start_time": 1.5,
                "end_time": 3.8,
                "frame_index": 45,
                "traffic_sign": {
                    "sign_Code": "P.123",
                    "name": "Cấm đi ngược chiều",
                    "description": "Biển báo cấm các phương tiện đi ngược chiều...",
                    "category": "Biển cấm",
                    "image_url": "https://example.com/sign.jpg",
                    "penalty_details": "Phạt 4-6 triệu đồng, tước GPLX 1-3 tháng",
                    "model_class_id": "2"
                }
            },
            {
                "id": 3,
                "class_id": 38,
                "class_name": "Giới hạn tốc độ (50km/h)",
                "confidence": 0.89,
                "bbox": [320.1, 150.5, 420.3, 250.8],
                "start_time": 5.2,
                "end_time": 8.7,
                "frame_index": 156,
                "traffic_sign": {
                    "sign_Code": "P.127",
                    "name": "Giới hạn tốc độ tối đa cho phép",
                    "description": "Biển báo giới hạn tốc độ tối đa...",
                    "category": "Biển cấm",
                    "image_url": "https://example.com/speed50.jpg",
                    "penalty_details": "Phạt từ 2-3 triệu đồng tùy mức độ vi phạm",
                    "model_class_id": "38"
                }
            }
        ]
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Lỗi khi xử lý: [Chi tiết lỗi]",
    "detection_id": 3
}
```

**Status Codes:**
- `201 Created`: Nhận diện thành công
- `400 Bad Request`: Thiếu file hoặc file_type không hợp lệ
- `500 Internal Server Error`: Lỗi khi xử lý file

---

### 2. Xem Chi Tiết Detection

**Endpoint:** `GET /api/recognition/detection/<detection_id>/`

**Example Request:**
```bash
curl http://localhost:8000/api/recognition/detection/1/
```

**Response:** Giống như response của endpoint upload-run

---

### 3. Xem Lịch Sử Nhận Diện (Legacy)

**Endpoint:** `GET /api/recognition/history/`

**Authentication:** Required (nếu user đã đăng nhập)

**Example Request:**
```bash
curl -H "Authorization: Bearer <your_token>" \
     http://localhost:8000/api/recognition/history/
```

---

## Cấu Trúc Response Chi Tiết

### DetectedSign Object (Biển báo phát hiện được)

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | ID của detected sign |
| `class_id` | integer | ID class từ YOLO model (0-51) |
| `class_name` | string | Tên biển báo từ YOLO model |
| `confidence` | float | Độ tin cậy (0.0 - 1.0) |
| `bbox` | array | Bounding box [x1, y1, x2, y2] |
| `start_time` | float/null | Thời gian bắt đầu xuất hiện (giây) - chỉ cho video |
| `end_time` | float/null | Thời gian kết thúc xuất hiện (giây) - chỉ cho video |
| `frame_index` | integer/null | Số frame đầu tiên xuất hiện |
| `traffic_sign` | object/null | Thông tin chi tiết biển báo từ database |

### TrafficSign Object (Thông tin biển báo)

| Field | Type | Description |
|-------|------|-------------|
| `sign_Code` | string | Mã biển báo (VD: P.123) |
| `name` | string | Tên đầy đủ biển báo |
| `description` | string | Mô tả chi tiết |
| `category` | string | Loại biển báo (Biển cấm, Biển báo nguy hiểm, ...) |
| `image_url` | string | URL hình ảnh biển báo chuẩn |
| `penalty_details` | string | Thông tin hình phạt vi phạm |
| `model_class_id` | string | ID class ánh xạ với YOLO model |

---

## Lưu Ý Quan Trọng

### 1. Timeline Detection cho Video
- API tự động gộp các detection liên tục của cùng một biển báo thành một khoảng thời gian
- Nếu một biển báo xuất hiện từ frame 45 đến frame 114 với FPS 30, nó sẽ được báo cáo là xuất hiện từ giây 1.5 đến giây 3.8
- Confidence là giá trị trung bình của tất cả detections trong khoảng thời gian đó

### 2. Mapping với TrafficSign Database
- API tự động tìm kiếm TrafficSign dựa trên `model_class_id` hoặc `name`
- Nếu không tìm thấy mapping, `traffic_sign` sẽ là `null`
- Đảm bảo bảng TrafficSign có trường `model_class_id` khớp với class_id từ YOLO

### 3. Output Files
- Ảnh/video output được lưu trong thư mục `media/results/`
- Output có vẽ bounding boxes và labels lên các biển báo phát hiện được
- Access qua `output_file_url` trong response

### 4. Performance
- Xử lý video có thể mất thời gian tùy thuộc vào độ dài video
- Mặc định xử lý mọi frame, có thể điều chỉnh `frame_stride` trong code để tăng tốc

### 5. YOLO Model Configuration
- Model weights: `ai_engine/YOLO11/best.pt`
- Confidence threshold: 0.25 (có thể điều chỉnh trong code)
- Số classes: 52 loại biển báo giao thông

---

## Testing API

### Test với Postman
1. Tạo new request với method POST
2. URL: `http://localhost:8000/api/recognition/upload-run/`
3. Body > form-data:
   - Key: `file`, Type: File, Value: chọn file ảnh/video
   - Key: `file_type`, Type: Text, Value: `image` hoặc `video`
4. Send request

### Test với Python
```python
import requests
import json

def test_image_detection(image_path):
    url = "http://localhost:8000/api/recognition/upload-run/"
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'file_type': 'image'}
        response = requests.post(url, files=files, data=data)
    
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result['success']:
        print(f"\nĐã phát hiện {len(result['data']['detected_signs'])} biển báo:")
        for sign in result['data']['detected_signs']:
            print(f"- {sign['class_name']} (confidence: {sign['confidence']:.2f})")
            if sign['traffic_sign']:
                print(f"  Mã: {sign['traffic_sign']['sign_Code']}")
                print(f"  Hình phạt: {sign['traffic_sign']['penalty_details']}")

def test_video_detection(video_path):
    url = "http://localhost:8000/api/recognition/upload-run/"
    with open(video_path, 'rb') as f:
        files = {'file': f}
        data = {'file_type': 'video'}
        response = requests.post(url, files=files, data=data)
    
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result['success']:
        print(f"\nVideo: {result['data']['duration']:.1f}s, FPS: {result['data']['fps']}")
        print(f"Phát hiện {len(result['data']['detected_signs'])} biển báo:")
        for sign in result['data']['detected_signs']:
            print(f"- {sign['class_name']} (confidence: {sign['confidence']:.2f})")
            print(f"  Xuất hiện từ giây {sign['start_time']:.1f} đến {sign['end_time']:.1f}")
            if sign['traffic_sign']:
                print(f"  Mã: {sign['traffic_sign']['sign_Code']}")

# Test
# test_image_detection('path/to/image.jpg')
# test_video_detection('path/to/video.mp4')
```

---

## Troubleshooting

### Lỗi "Cannot find YOLO weight file"
- Kiểm tra file `ai_engine/YOLO11/best.pt` có tồn tại
- Hoặc set biến môi trường `YOLO_WEIGHTS` trong `.env`

### Lỗi "traffic_sign is null"
- Cần cập nhật bảng TrafficSign với trường `model_class_id` 
- Chạy script mapping: `python scripts/add_sign_metadata.py` (nếu có)
- Hoặc manually update `model_class_id` trong TrafficSign để khớp với class_id của YOLO

### Video processing quá chậm
- Tăng `frame_stride` trong `views.py` để skip một số frames
- Giảm resolution video trước khi upload
- Giảm confidence threshold để ít detections hơn

---

## Database Schema Changes

Migration đã tạo các thay đổi sau:

### Detection Model
- Thêm: `user`, `fps`, `duration`, `total_frames`
- Cập nhật: `status` choices (thêm "processing")
- Xóa: `result` field (deprecated)

### DetectedSign Model (Mới)
- Lưu chi tiết từng biển báo phát hiện được
- Support timeline cho video (start_time, end_time)
- Link với TrafficSign để lấy thông tin chi tiết

---

## Next Steps

### Cải tiến có thể thêm:
1. **Authentication**: Thêm authentication cho endpoints
2. **Rate Limiting**: Giới hạn số requests để tránh overload
3. **Async Processing**: Xử lý video bất đồng bộ với Celery
4. **Webhooks**: Notify khi xử lý video hoàn tất
5. **Statistics**: API để xem thống kê các biển báo phát hiện được
6. **Model Versioning**: Support multiple YOLO model versions
7. **Batch Processing**: Upload và xử lý nhiều files cùng lúc

### Database optimization:
1. Index các trường thường query (`created_at`, `status`, `user_id`)
2. Archiving detection cũ để giảm database size
3. Caching traffic_sign information
