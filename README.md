1. Chuẩn bị môi trường
* Tạo môi trường ảo (ví dụ tên là 'venv')
``` bash
python -m venv venv
```
* Kích hoạt môi trường ảo
Trên Windows:
```bash
.\venv\Scripts\activate
```
Trên macOS/Linux:
``` bash
source venv/bin/activate
```
## Lệnh hữu ích
 tạo schema cho db
```bash
python manage.py makemigrations
python manage.py migrate
```


## các thư viện cần thiết
- pip install djangorestframework
- pip install djangorestframework-simplejwt  # Cho xác thực JWT
- pip install django-cors-headers           # Cho phép React gọi API
- pip install mssql-django                  # Driver kết nối với SQL Server
- pip install python-decouple               # Quản lý biến môi trường (an toàn hơn)
- pip install Pillow                        # Xử lý ảnh

**Các thư viện cho AI Engine:**
1. Cài đặt PyTorch trước tiên (truy cập https://pytorch.org/get-started/locally/ để có lệnh chính xác nhất cho hệ điều hành của bạn)
* Ví dụ cho Windows/Linux với CUDA:
* pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
2. Cài đặt YOLOv8 và OpenCV
```bash
pip install ultralytics opencv-python-headless
```