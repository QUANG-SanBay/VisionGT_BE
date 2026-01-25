import os
from pathlib import Path
import django

import sys
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visionGT_BE.settings")
django.setup()

from traffic_signs.models import TrafficSign  # noqa: E402

# Metadata đầy đủ cho 52 loại biển báo từ YOLO model (class_id: 0-51)
# Bạn có thể bổ sung thêm thông tin vào các field: description, penalty_details
SIGN_METADATA = {
    "W-224": {
        "model_class_id": "0",
        "name": "Đường người đi bộ cắt ngang",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp tới phần đường dành cho người đi bộ sang qua đường. Gặp biển này các xe phải giảm tốc độ, nhường ưu tiên cho người đi bộ.",
        "penalty_details": "Không nhường đường cho người đi bộ: Phạt 200.000 - 400.000 đồng (xe máy), 200.000 - 400.000 đồng (ô tô)."
    },
    "W-205d": {
        "model_class_id": "1",
        "name": "Đường giao nhau (ngã ba bên phải)",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến nơi giao nhau cùng mức của các tuyến đường cùng cấp (không có đường nào ưu tiên) trên cùng một mặt bằng.",
        "penalty_details": ""
    },
    "P-102": {
        "model_class_id": "2",
        "name": "Cấm đi ngược chiều",
        "category": "Biển cấm",
        "description": "Báo đường cấm các loại xe (cơ giới và thô sơ) đi vào theo chiều đặt biển, trừ các xe được ưu tiên theo quy định.",
        "penalty_details": "Phạt 1.000.000 - 2.000.000 đồng (xe máy); 4.000.000 - 6.000.000 đồng, tước GPLX 2-4 tháng (ô tô)."
    },
    "R-302a": {
        "model_class_id": "3",
        "name": "Hướng phải đi vòng chướng ngại vật (sang phải)",
        "category": "Biển hiệu lệnh",
        "description": "Báo các loại xe (cơ giới và thô sơ) hướng đi vòng sang phải để qua một chướng ngại vật.",
        "penalty_details": "Không chấp hành hiệu lệnh: Phạt 400.000 - 600.000 đồng (xe máy); 4.000.000 - 6.000.000 đồng (ô tô)."
    },
    "W-205a": {
        "model_class_id": "4",
        "name": "Đường giao nhau cùng cấp",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến nơi giao nhau cùng mức của các tuyến đường cùng cấp (không có đường nào ưu tiên) trên cùng một mặt bằng.",
        "penalty_details": ""
    },
    "W-207a": {
        "model_class_id": "5",
        "name": "Giao nhau với đường không ưu tiên",
        "category": "Biển báo nguy hiểm",
        "description": "Đặt trên đường ưu tiên để báo trước sắp đến nơi giao nhau với đường không ưu tiên. Xe đi trên đường này được quyền ưu tiên qua nơi giao nhau.",
        "penalty_details": ""
    },
    "W-201a": {
        "model_class_id": "6",
        "name": "Chỗ ngoặt nguy hiểm vòng bên trái",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến một chỗ ngoặt nguy hiểm vòng bên trái.",
        "penalty_details": ""
    },
    "P-123a": {
        "model_class_id": "7",
        "name": "Cấm rẽ trái",
        "category": "Biển cấm",
        "description": "Báo cấm rẽ trái (theo hướng mũi tên chỉ) ở những vị trí đường giao nhau. Biển không có giá trị cấm quay đầu xe.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (xe máy); 800.000 - 1.000.000 đồng (ô tô)."
    },
    "R-434": {
        "model_class_id": "8",
        "name": "Bến xe buýt",
        "category": "Biển chỉ dẫn",
        "description": "Chỉ dẫn chỗ dừng đỗ xe buýt cho khách lên xuống.",
        "penalty_details": ""
    },
    "R-303": {
        "model_class_id": "9",
        "name": "Nơi giao nhau chạy theo vòng xuyến",
        "category": "Biển hiệu lệnh",
        "description": "Báo cho các loại xe (thô sơ và cơ giới) phải chạy vòng theo đảo an toàn ở nơi đường giao nhau.",
        "penalty_details": "Không tuân thủ quy tắc nhường đường tại vòng xuyến: Phạt 400.000 - 600.000 đồng (xe máy); 800.000 - 1.000.000 đồng (ô tô)."
    },
    "P-130": {
        "model_class_id": "10",
        "name": "Cấm dừng xe và đỗ xe",
        "category": "Biển cấm",
        "description": "Báo nơi cấm dừng xe và đỗ xe. Biển có hiệu lực cấm các loại xe cơ giới dừng và đỗ ở phía đường có đặt biển.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (xe máy); 400.000 - 600.000 đồng (ô tô) đối với hành vi dừng đỗ sai quy định."
    },
    "R-409": {
        "model_class_id": "11",
        "name": "Chỗ quay xe",
        "category": "Biển chỉ dẫn",
        "description": "Chỉ dẫn vị trí được phép quay đầu xe.",
        "penalty_details": ""
    },
    "S-509a": {
        "model_class_id": "12",
        "name": "Thuyết minh biển chính",
        "category": "Biển phụ",
        "description": "Biển phụ dùng để thuyết minh bổ sung cho biển chính (ví dụ: Chiều cao an toàn, Cấm đỗ xe...).",
        "penalty_details": ""
    },
    "W-245a": {
        "model_class_id": "13",
        "name": "Đi chậm",
        "category": "Biển báo nguy hiểm",
        "description": "Nhắc lái xe giảm tốc độ đi chậm.",
        "penalty_details": ""
    },
    "P-106a": {
        "model_class_id": "14",
        "name": "Cấm xe ô tô tải",
        "category": "Biển cấm",
        "description": "Báo đường cấm các loại xe ô tô tải trừ các xe được ưu tiên theo quy định. Biển có hiệu lực cấm đối với cả máy kéo và các xe máy chuyên dùng.",
        "penalty_details": "Phạt 1.000.000 - 2.000.000 đồng, tước GPLX 1-3 tháng."
    },
    "W-203c": {
        "model_class_id": "15",
        "name": "Đường bị thu hẹp về phía phải",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến một đoạn đường bị thu hẹp đột ngột về phía phải.",
        "penalty_details": ""
    },
    "P-117": {
        "model_class_id": "16",
        "name": "Hạn chế chiều cao",
        "category": "Biển cấm",
        "description": "Báo hạn chế chiều cao của xe. Cấm các xe (cơ giới và thô sơ) có chiều cao vượt quá trị số ghi trên biển đi qua.",
        "penalty_details": "Phạt 2.000.000 - 3.000.000 đồng, tước GPLX 1-3 tháng."
    },
    "P-124a": {
        "model_class_id": "17",
        "name": "Cấm quay đầu xe",
        "category": "Biển cấm",
        "description": "Báo cấm các loại xe quay đầu (theo kiểu chữ U). Chiều mũi tên phù hợp với chiều cấm quay đầu xe. Biển không có giá trị cấm rẽ trái.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (xe máy); 400.000 - 600.000 đồng (ô tô)."
    },
    "P-107a": {
        "model_class_id": "18",
        "name": "Cấm xe ô tô khách",
        "category": "Biển cấm",
        "description": "Báo đường cấm ô tô chở khách đi qua trừ các xe ưu tiên theo quy định. Biển này không cấm xe buýt.",
        "penalty_details": "Phạt 1.000.000 - 2.000.000 đồng, tước GPLX 1-3 tháng."
    },
    "P-137": {
        "model_class_id": "19",
        "name": "Cấm rẽ trái, rẽ phải",
        "category": "Biển cấm",
        "description": "Các ngả đường phía trước cấm tất cả các loại xe (trừ xe ưu tiên theo quy định) rẽ trái hay rẽ phải.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (xe máy); 800.000 - 1.000.000 đồng (ô tô)."
    },
    "P-103a": {
        "model_class_id": "20",
        "name": "Cấm xe ô tô",
        "category": "Biển cấm",
        "description": "Báo đường cấm các loại xe cơ giới kể cả xe máy 3 bánh có thùng đi qua, trừ xe máy 2 bánh, xe gắn máy và các xe được ưu tiên.",
        "penalty_details": "Phạt 1.000.000 - 2.000.000 đồng, tước GPLX 1-3 tháng."
    },
    "W-203b": {
        "model_class_id": "21",
        "name": "Đường bị thu hẹp về phía trái",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến một đoạn đường bị thu hẹp đột ngột về phía trái.",
        "penalty_details": ""
    },
    "W-219": {
        "model_class_id": "22",
        "name": "Dốc xuống nguy hiểm",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp tới đoạn đường xuống dốc nguy hiểm.",
        "penalty_details": ""
    },
    "P-112": {
        "model_class_id": "23",
        "name": "Cấm người đi bộ",
        "category": "Biển cấm",
        "description": "Báo đường cấm người đi bộ qua lại.",
        "penalty_details": "Phạt người đi bộ 60.000 - 100.000 đồng."
    },
    "W-227": {
        "model_class_id": "24",
        "name": "Công trường",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước gần tới đoạn đường đang tiến hành thi công sửa chữa, cải tạo, nâng cấp có người và máy móc đang làm việc.",
        "penalty_details": ""
    },
    "AUTO-025": {
        "model_class_id": "25",
        "name": "Chỉ dành cho xe máy (R.403e)",
        "category": "Biển hiệu lệnh",
        "description": "Báo hiệu bắt đầu đường dành cho xe máy.",
        "penalty_details": "Đi sai làn đường: Phạt 400.000 - 600.000 đồng (xe máy)."
    },
    "W-233a": {
        "model_class_id": "26",
        "name": "Nguy hiểm khác",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trên đường có những nguy hiểm mà không thể vận dụng được các kiểu biển báo nguy hiểm khác.",
        "penalty_details": ""
    },
    "W-225": {
        "model_class_id": "27",
        "name": "Trẻ em",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước là gần đến đoạn đường thường có trẻ em đi ngang qua hoặc tụ tập trên đường.",
        "penalty_details": ""
    },
    "AUTO-028": {
        "model_class_id": "28",
        "name": "Làn đường dành cho xe tải và xe công",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu làn đường hoặc đường dành riêng cho xe tải và xe công trình.",
        "penalty_details": "Đi sai làn đường: Phạt 4.000.000 - 6.000.000 đồng, tước GPLX 1-3 tháng (ô tô)."
    },
    "P-104-29": {
        "model_class_id": "29",
        "name": "Cấm xe máy",
        "category": "Biển cấm",
        "description": "Báo đường cấm các loại xe máy, trừ các xe được ưu tiên theo quy định. Biển không có giá trị cấm những người dắt xe máy.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng, tước GPLX 1-3 tháng."
    },
    "AUTO-030": {
        "model_class_id": "30",
        "name": "Làn đường dành cho xe tải (R.412c)",
        "category": "Biển hiệu lệnh",
        "description": "Làn đường dành riêng cho xe ôtô tải.",
        "penalty_details": "Đi sai làn đường: Phạt 4.000.000 - 6.000.000 đồng, tước GPLX 1-3 tháng (ô tô)."
    },
    "AUTO-031": {
        "model_class_id": "31",
        "name": "Đường có camera giám sát",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu đoạn đường có lắp đặt hệ thống camera giám sát giao thông.",
        "penalty_details": ""
    },
    "P-123b": {
        "model_class_id": "32",
        "name": "Cấm rẽ phải",
        "category": "Biển cấm",
        "description": "Báo cấm rẽ phải (theo hướng mũi tên chỉ) ở những vị trí đường giao nhau. Biển không có giá trị cấm quay đầu xe.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (xe máy); 800.000 - 1.000.000 đồng (ô tô)."
    },
    "W-202a": {
        "model_class_id": "33",
        "name": "Nhiều chỗ ngoặt nguy hiểm liên tiếp (trái)",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến hai chỗ ngoặt ngược chiều nhau liên tiếp, trong đó chỗ ngoặt đầu tiên hướng vòng bên trái.",
        "penalty_details": ""
    },
    "P-106b": {
        "model_class_id": "34",
        "name": "Cấm xe ô tô tải (theo trọng lượng)",
        "category": "Biển cấm",
        "description": "Báo đường cấm các loại xe ô tô tải có khối lượng chuyên chở (theo Giấy chứng nhận kiểm định) lớn hơn giá trị chữ số ghi trong biển.",
        "penalty_details": "Phạt 1.000.000 - 2.000.000 đồng, tước GPLX 1-3 tháng."
    },
    "AUTO-035": {
        "model_class_id": "35",
        "name": "Cấm rẽ trái và rẽ phải (P.137)",
        "category": "Biển cấm",
        "description": "Các ngả đường phía trước cấm tất cả các loại xe (trừ xe ưu tiên theo quy định) rẽ trái hay rẽ phải.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (xe máy); 800.000 - 1.000.000 đồng (ô tô)."
    },
    "AUTO-036": {
        "model_class_id": "36",
        "name": "Cấm đi thẳng và rẽ phải (P.139)",
        "category": "Biển cấm",
        "description": "Biểu thị đường qua nút giao cấm tất cả các loại xe (trừ xe ưu tiên) đi thẳng và rẽ phải.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (xe máy); 800.000 - 1.000.000 đồng (ô tô)."
    },
    "W-205c": {
        "model_class_id": "37",
        "name": "Đường giao nhau (ngã ba bên trái)",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến nơi giao nhau cùng mức của các tuyến đường cùng cấp (không có đường nào ưu tiên) trên cùng một mặt bằng.",
        "penalty_details": ""
    },
    "P-127-50": {
        "model_class_id": "38",
        "name": "Tốc độ tối đa cho phép (50km/h)",
        "category": "Biển cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy là 50km/h.",
        "penalty_details": "Vượt 5-10km/h: 300k-400k (xe máy), 800k-1tr (ô tô); 10-20km/h: 800k-1tr (xe máy), 4tr-6tr (ô tô); >20km/h: phạt cao hơn + tước GPLX."
    },
    "P-127-60": {
        "model_class_id": "39",
        "name": "Tốc độ tối đa cho phép (60km/h)",
        "category": "Biển cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy là 60km/h.",
        "penalty_details": "Vượt 5-10km/h: 300k-400k (xe máy), 800k-1tr (ô tô); 10-20km/h: 800k-1tr (xe máy), 4tr-6tr (ô tô); >20km/h: phạt cao hơn + tước GPLX."
    },
    "P-127-80": {
        "model_class_id": "40",
        "name": "Tốc độ tối đa cho phép (80km/h)",
        "category": "Biển cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy là 80km/h.",
        "penalty_details": "Vượt 5-10km/h: 300k-400k (xe máy), 800k-1tr (ô tô); 10-20km/h: 800k-1tr (xe máy), 4tr-6tr (ô tô); >20km/h: phạt cao hơn + tước GPLX."
    },
    "P-127-40": {
        "model_class_id": "41",
        "name": "Tốc độ tối đa cho phép (40km/h)",
        "category": "Biển cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy là 40km/h.",
        "penalty_details": "Vượt 5-10km/h: 300k-400k (xe máy), 800k-1tr (ô tô); 10-20km/h: 800k-1tr (xe máy), 4tr-6tr (ô tô); >20km/h: phạt cao hơn + tước GPLX."
    },
    "R-301d": {
        "model_class_id": "42",
        "name": "Các xe chỉ được rẽ phải",
        "category": "Biển hiệu lệnh",
        "description": "Báo các xe chỉ được rẽ phải. Biển được đặt ở trước nơi đường giao nhau.",
        "penalty_details": "Không chấp hành hiệu lệnh: Phạt 400.000 - 600.000 đồng (xe máy); 4.000.000 - 6.000.000 đồng (ô tô)."
    },
    "AUTO-043": {
        "model_class_id": "43",
        "name": "Chiều cao tĩnh không thực tế (W.239b)",
        "category": "Biển báo nguy hiểm",
        "description": "Báo chiều cao tĩnh không thực tế của các vị trí có khoảng cách từ điểm cao nhất của mặt đường đến điểm thấp nhất của chướng ngại vật bị giới hạn.",
        "penalty_details": ""
    },
    "W-233": {
        "model_class_id": "44",
        "name": "Nguy hiểm khác",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trên đường có những nguy hiểm mà không thể vận dụng được các kiểu biển báo nguy hiểm khác.",
        "penalty_details": ""
    },
    "R-407a": {
        "model_class_id": "45",
        "name": "Đường một chiều",
        "category": "Biển chỉ dẫn",
        "description": "Chỉ dẫn những đoạn đường chạy một chiều. Chỉ cho phép các loại phương tiện giao thông đi theo chiều vào theo mũi tên chỉ.",
        "penalty_details": "Đi ngược chiều: Phạt 1.000.000 - 2.000.000 đồng (xe máy); 4.000.000 - 6.000.000 đồng (ô tô)."
    },
    "P-131a": {
        "model_class_id": "46",
        "name": "Cấm đỗ xe",
        "category": "Biển cấm",
        "description": "Báo nơi cấm đỗ xe. Biển có hiệu lực cấm các loại xe cơ giới đỗ ở phía đường có đặt biển.",
        "penalty_details": "Phạt 300.000 - 400.000 đồng (xe máy); 800.000 - 1.000.000 đồng (ô tô)."
    },
    "P-124b": {
        "model_class_id": "47",
        "name": "Cấm ô tô quay đầu xe",
        "category": "Biển cấm",
        "description": "Báo cấm xe ô tô và xe máy 3 bánh (side car) quay đầu (theo kiểu chữ U). Chiều mũi tên phù hợp với chiều cấm xe ô tô quay đầu.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (ô tô)."
    },
    "W-210": {
        "model_class_id": "48",
        "name": "Giao nhau với đường sắt có rào chắn",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến chỗ giao nhau giữa đường bộ và đường sắt có rào chắn kín hay rào chắn nửa kín và có nhân viên ngành đường sắt điều khiển.",
        "penalty_details": "Vượt rào chắn đường sắt: Phạt 6.000.000 - 8.000.000 đồng, tước GPLX 2-4 tháng (ô tô); 2.000.000 - 3.000.000 đồng (xe máy)."
    },
    "P-124c": {
        "model_class_id": "49",
        "name": "Cấm rẽ trái và quay đầu xe",
        "category": "Biển cấm",
        "description": "Báo cấm các loại xe rẽ trái đồng thời cấm quay đầu.",
        "penalty_details": "Phạt 400.000 - 600.000 đồng (xe máy); 800.000 - 1.000.000 đồng (ô tô)."
    },
    "W-201b": {
        "model_class_id": "50",
        "name": "Chỗ ngoặt nguy hiểm vòng bên phải",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến một chỗ ngoặt nguy hiểm vòng bên phải.",
        "penalty_details": ""
    },
    "R-302b": {
        "model_class_id": "51",
        "name": "Hướng phải đi vòng chướng ngại vật (sang phải)",
        "category": "Biển hiệu lệnh",
        "description": "Báo các loại xe (cơ giới và thô sơ) hướng đi vòng sang phải để qua một chướng ngại vật.",
        "penalty_details": "Không chấp hành hiệu lệnh: Phạt 400.000 - 600.000 đồng (xe máy); 4.000.000 - 6.000.000 đồng (ô tô)."
    }
}


def run():
    """
    Populate TrafficSign database với metadata đầy đủ
    Chạy script này sau khi migrate để có data sẵn
    """
    created = 0
    updated = 0
    
    for sign_code, meta in SIGN_METADATA.items():
        obj, is_created = TrafficSign.objects.get_or_create(
            sign_Code=sign_code,
            defaults={
                "name": meta.get("name", sign_code),
                "category": meta.get("category", ""),
                "description": meta.get("description", ""),
                "penalty_details": meta.get("penalty_details", ""),
                "model_class_id": meta.get("model_class_id"),
            }
        )
        
        if is_created:
            created += 1
            print(f"✅ Created: {sign_code} - {meta['name']}")
        else:
            # Cập nhật nếu đã tồn tại
            obj.name = meta.get("name", obj.name)
            obj.category = meta.get("category", obj.category)
            obj.description = meta.get("description", obj.description)
            obj.penalty_details = meta.get("penalty_details", obj.penalty_details)
            if meta.get("model_class_id"):
                obj.model_class_id = meta["model_class_id"]
            obj.save()
            updated += 1
            print(f"✏️  Updated: {sign_code} - {meta['name']}")
    
    print("\n" + "="*60)
    print(f"📊 HOÀN THÀNH!")
    print(f"  ✅ Tạo mới: {created}")
    print(f"  ✏️  Cập nhật: {updated}")
    print(f"  📝 Tổng: {len(SIGN_METADATA)} biển báo")
    print("="*60)
    
    # Verify mapping
    total_signs = TrafficSign.objects.count()
    signs_with_model_id = TrafficSign.objects.exclude(model_class_id__isnull=True).exclude(model_class_id='').count()
    
    print(f"\n📈 THỐNG KÊ DATABASE:")
    print(f"  Tổng số biển báo: {total_signs}")
    print(f"  Có model_class_id: {signs_with_model_id}")
    print(f"  Chưa có model_class_id: {total_signs - signs_with_model_id}")
    
    if signs_with_model_id >= 52:
        print("\n🎉 ĐÃ MAPPING ĐỦ 52 CLASSES TỪ YOLO MODEL!")
    else:
        print(f"\n⚠️  Còn thiếu {52 - signs_with_model_id} classes chưa mapping")


if __name__ == "__main__":
    run()
