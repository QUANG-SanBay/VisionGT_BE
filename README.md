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
1. Cài đặt toàn bộ thư viện trong 1 lệnh
```bash
pip install -r requirements.txt
```
2. Tạo schema cho db
```bash
python manage.py makemigrations
python manage.py migrate users
python manage.py migrate token_blacklist 0007
python manage.py migrate token_blacklist 0008 --fake
python manage.py migrate
python scripts/load_classes.py
python scripts/add_sign_metadata.py
```
> **Lưu ý**: Migration `token_blacklist 0008` cần dùng `--fake` vì có vấn đề tương thích với SQL Server constraints.
3. Runserver
```bash 
python manage.py runserver
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