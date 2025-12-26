from roboflow import Roboflow

# Khởi tạo Roboflow với API Key (Bạn có thể lấy key miễn phí tại roboflow.com)
rf = Roboflow(api_key="Pn0LTQCnELXAqVr44c3f")
project = rf.workspace("vietnam-traffic-sign-detection").project("vietnam-traffic-sign-detection-2i2j8")

# Tải phiên bản model bạn muốn (ví dụ phiên bản 1)
# Model sẽ được lưu vào thư mục cục bộ
version = project.version(1)
model = version.model

# Tải file weights về máy
model.download("pt")
