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
        "description": "Báo trước sắp tới phần đường dành cho người đi bộ sang đường. Các xe phải giảm tốc độ, nhường ưu tiên cho người đi bộ.",
        "penalty_details": "Không nhường đường: phạt 400k-600k đồng"
    },
    "W-205d": {
        "model_class_id": "1",
        "name": "Đường giao nhau (ngã ba bên phải)",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến nơi giao nhau hình chữ T, đường chính đi thẳng và giao với đường phụ từ bên phải.",
        "penalty_details": ""
    },
    "P-102": {
        "model_class_id": "2",
        "name": "Cấm đi ngược chiều",
        "category": "Biển cấm",
        "description": "Báo đường cấm tất cả các loại xe đi vào theo chiều đặt biển, trừ các xe được ưu tiên theo quy định.",
        "penalty_details": "Phạt 4-6 triệu đồng, tước GPLX 1-3 tháng"
    },
    "R-302a": {
        "model_class_id": "3",
        "name": "Phải đi vòng sang bên phải",
        "category": "Biển hiệu lệnh",
        "description": "Báo cho các loại xe phải vòng sang bên phải để tránh chướng ngại vật.",
        "penalty_details": ""
    },
    "W-205a": {
        "model_class_id": "4",
        "name": "Giao nhau với đường đồng cấp",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến nơi giao nhau của các tuyến đường cùng cấp (không có đường nào ưu tiên).",
        "penalty_details": ""
    },
    "W-207a": {
        "model_class_id": "5",
        "name": "Giao nhau với đường không ưu tiên",
        "category": "Biển báo nguy hiểm",
        "description": "Đặt trên đường ưu tiên để báo trước sắp đến nơi giao nhau với đường không ưu tiên.",
        "penalty_details": ""
    },
    "W-201a": {
        "model_class_id": "6",
        "name": "Chỗ ngoặt nguy hiểm vòng bên trái",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến một chỗ ngoặt nguy hiểm vòng về bên trái.",
        "penalty_details": ""
    },
    "P-123a": {
        "model_class_id": "7",
        "name": "Cấm rẽ trái",
        "category": "Biển cấm",
        "description": "Báo cấm các loại xe rẽ trái ở những nơi đường giao nhau, trừ các xe được ưu tiên theo quy định.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "R-434": {
        "model_class_id": "8",
        "name": "Bến xe buýt",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu vị trí bến xe buýt.",
        "penalty_details": ""
    },
    "R-303": {
        "model_class_id": "9",
        "name": "Nơi giao nhau chạy theo vòng xuyến",
        "category": "Biển hiệu lệnh",
        "description": "Báo cho các loại xe phải chạy vòng theo đảo an toàn ở nơi đường giao nhau.",
        "penalty_details": ""
    },
    "P-130": {
        "model_class_id": "10",
        "name": "Cấm dừng và đỗ xe",
        "category": "Biển cấm",
        "description": "Báo nơi cấm dừng xe và đỗ xe. Biển có hiệu lực cấm các loại xe cơ giới dừng và đỗ ở phía đường có đặt biển.",
        "penalty_details": "Phạt 300k-400k đồng"
    },
    "R-409": {
        "model_class_id": "11",
        "name": "Chỗ quay xe",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu vị trí được phép quay đầu xe.",
        "penalty_details": ""
    },
    "S-509a": {
        "model_class_id": "12",
        "name": "Biển gộp làn đường theo phương tiện",
        "category": "Biển phụ",
        "description": "Biển phụ chỉ dẫn làn đường cho từng loại phương tiện.",
        "penalty_details": ""
    },
    "W-245a": {
        "model_class_id": "13",
        "name": "Đi chậm",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước cho người tham gia giao thông biết sắp đến đoạn đường cần phải giảm tốc độ.",
        "penalty_details": ""
    },
    "P-106a": {
        "model_class_id": "14",
        "name": "Cấm xe tải",
        "category": "Biển cấm",
        "description": "Báo đường cấm các loại xe ô tô tải, trừ các xe được ưu tiên theo quy định.",
        "penalty_details": "Phạt 800k-1 triệu đồng"
    },
    "W-203c": {
        "model_class_id": "15",
        "name": "Đường bị thu hẹp về phía phải",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước đoạn đường bị hẹp lại ở phía bên phải.",
        "penalty_details": ""
    },
    "P-117": {
        "model_class_id": "16",
        "name": "Giới hạn chiều cao",
        "category": "Biển cấm",
        "description": "Báo cấm các xe có chiều cao (tính cả xe và hàng hóa) vượt quá trị số ghi trên biển đi qua.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "P-124a": {
        "model_class_id": "17",
        "name": "Cấm quay đầu",
        "category": "Biển cấm",
        "description": "Báo cấm các loại xe quay đầu xe theo kiểu chữ U, trừ các xe được ưu tiên theo quy định.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "P-107a": {
        "model_class_id": "18",
        "name": "Cấm ô tô khách và ô tô tải",
        "category": "Biển cấm",
        "description": "Báo đường cấm ô tô chở khách và ô tô tải đi qua trừ các xe ưu tiên theo quy định.",
        "penalty_details": ""
    },
    "P-137": {
        "model_class_id": "19",
        "name": "Cấm rẽ phải và quay đầu",
        "category": "Biển cấm",
        "description": "Báo cấm các loại xe rẽ phải đồng thời cấm quay đầu xe.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "P-103a": {
        "model_class_id": "20",
        "name": "Cấm ô tô",
        "category": "Biển cấm",
        "description": "Báo đường cấm tất cả các loại xe cơ giới, kể cả xe mô tô 3 bánh có thùng đi qua.",
        "penalty_details": "Phạt 800k-1 triệu đồng"
    },
    "W-203b": {
        "model_class_id": "21",
        "name": "Đường bị thu hẹp về phía trái",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước đoạn đường bị hẹp lại ở phía bên trái.",
        "penalty_details": ""
    },
    "W-219": {
        "model_class_id": "22",
        "name": "Gồ giảm tốc phía trước",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp tới dốc xuống nguy hiểm. Người điều khiển phương tiện phải chọn cách chạy phù hợp.",
        "penalty_details": ""
    },
    "P-112": {
        "model_class_id": "23",
        "name": "Cấm xe hai và ba bánh",
        "category": "Biển cấm",
        "description": "Báo đường cấm tất cả các loại xe mô tô hai bánh, xe mô tô ba bánh và các loại xe tương tự đi qua.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "W-227": {
        "model_class_id": "24",
        "name": "Kiểm tra",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước gần tới đoạn đường có trạm kiểm tra, kiểm soát.",
        "penalty_details": ""
    },
    "AUTO-025": {
        "model_class_id": "25",
        "name": "Chỉ dành cho xe máy*",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu đường chỉ dành cho xe máy.",
        "penalty_details": ""
    },
    "W-233a": {
        "model_class_id": "26",
        "name": "Chướng ngoại vật phía trước",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước có chướng ngại vật phía trước, xe cần đi chậm và cẩn thận.",
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
        "name": "Xe tải và xe công*",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu đường dành cho xe tải và xe công trình.",
        "penalty_details": ""
    },
    "P-104-29": {
        "model_class_id": "29",
        "name": "Cấm mô tô và xe máy",
        "category": "Biển cấm",
        "description": "Báo đường cấm tất cả các loại xe mô tô đi qua, trừ các xe được ưu tiên theo quy định.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "AUTO-030": {
        "model_class_id": "30",
        "name": "Chỉ dành cho xe tải*",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu đường chỉ dành cho xe tải.",
        "penalty_details": ""
    },
    "AUTO-031": {
        "model_class_id": "31",
        "name": "Đường có camera giám sát",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu đoạn đường có camera giám sát giao thông.",
        "penalty_details": ""
    },
    "P-123b": {
        "model_class_id": "32",
        "name": "Cấm rẽ phải",
        "category": "Biển cấm",
        "description": "Báo cấm các loại xe rẽ phải ở những nơi đường giao nhau, trừ các xe được ưu tiên theo quy định.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "W-202a": {
        "model_class_id": "33",
        "name": "Nhiều chỗ ngoặt nguy hiểm liên tiếp, chỗ đầu tiên sang phải",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến nhiều chỗ ngoặt nguy hiểm liên tiếp, trong đó chỗ ngoặt đầu tiên vòng về bên phải.",
        "penalty_details": ""
    },
    "P-106b": {
        "model_class_id": "34",
        "name": "Cấm xe sơ-mi rơ-moóc",
        "category": "Biển cấm",
        "description": "Báo đường cấm các loại xe sơ-mi rơ-moóc đi qua.",
        "penalty_details": ""
    },
    "AUTO-035": {
        "model_class_id": "35",
        "name": "Cấm rẽ trái và phải",
        "category": "Biển cấm",
        "description": "Báo hiệu ở ngã đường phía trước cấm tất cả các loại xe rẽ trái hoặc rẽ phải.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "AUTO-036": {
        "model_class_id": "36",
        "name": "Cấm đi thẳng và rẽ phải",
        "category": "Biển cấm",
        "description": "Báo cấm các loại xe đi thẳng và rẽ phải.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "W-205c": {
        "model_class_id": "37",
        "name": "Đường giao nhau (ngã ba bên trái)",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến nơi giao nhau hình chữ T, đường chính đi thẳng và giao với đường phụ từ bên trái.",
        "penalty_details": ""
    },
    "P-127-50": {
        "model_class_id": "38",
        "name": "Giới hạn tốc độ (50km/h)",
        "category": "Biển cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy. Biển có hiệu lực cấm các xe cơ giới chạy với tốc độ vượt quá 50km/h.",
        "penalty_details": "Vượt 5-10km/h: 400k-600k; 10-20km/h: 800k-1tr; >20km/h: 2-3tr"
    },
    "P-127-60": {
        "model_class_id": "39",
        "name": "Giới hạn tốc độ (60km/h)",
        "category": "Biển cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy là 60km/h.",
        "penalty_details": "Vượt 5-10km/h: 400k-600k; 10-20km/h: 800k-1tr; >20km/h: 2-3tr"
    },
    "P-127-80": {
        "model_class_id": "40",
        "name": "Giới hạn tốc độ (80km/h)",
        "category": "Biển cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy là 80km/h.",
        "penalty_details": "Vượt 5-10km/h: 800k-1tr; 10-20km/h: 2-3tr; >20km/h: 4-6tr"
    },
    "P-127-40": {
        "model_class_id": "41",
        "name": "Giới hạn tốc độ (40km/h)",
        "category": "Biển cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy là 40km/h.",
        "penalty_details": "Vượt 5-10km/h: 400k-600k; 10-20km/h: 800k-1tr; >20km/h: 2-3tr"
    },
    "R-301d": {
        "model_class_id": "42",
        "name": "Các xe chỉ được rẽ trái",
        "category": "Biển hiệu lệnh",
        "description": "Báo hiệu các xe chỉ được rẽ trái. Biển đặt ở sau nơi đường giao nhau.",
        "penalty_details": ""
    },
    "AUTO-043": {
        "model_class_id": "43",
        "name": "Chiều cao tĩnh không thực tế",
        "category": "Biển báo nguy hiểm",
        "description": "Báo chiều cao an toàn tối đa của phương tiện khi đi qua.",
        "penalty_details": ""
    },
    "W-233": {
        "model_class_id": "44",
        "name": "Nguy hiểm khác",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước những nguy hiểm có thể xảy ra mà chưa có loại biển báo nào phù hợp để mô tả.",
        "penalty_details": ""
    },
    "R-407a": {
        "model_class_id": "45",
        "name": "Đường một chiều",
        "category": "Biển chỉ dẫn",
        "description": "Báo hiệu đường một chiều, chỉ cho phép các loại xe đi theo một chiều.",
        "penalty_details": ""
    },
    "P-131a": {
        "model_class_id": "46",
        "name": "Cấm đỗ xe",
        "category": "Biển cấm",
        "description": "Báo nơi cấm đỗ xe. Biển có hiệu lực cấm các loại xe cơ giới đỗ ở phía đường có đặt biển.",
        "penalty_details": "Phạt 200k-300k đồng"
    },
    "P-124b": {
        "model_class_id": "47",
        "name": "Cấm ô tô quay đầu xe (được rẽ trái)",
        "category": "Biển cấm",
        "description": "Báo cấm xe ô tô và xe mô tô 3 bánh quay đầu xe, nhưng được phép rẽ trái.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "W-210": {
        "model_class_id": "48",
        "name": "Giao nhau với đường sắt có rào chắn",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến chỗ giao nhau giữa đường bộ và đường sắt có rào chắn.",
        "penalty_details": "Vượt rào chắn: phạt 16-18 triệu đồng, tước GPLX 2-4 tháng"
    },
    "P-124c": {
        "model_class_id": "49",
        "name": "Cấm rẽ trái và quay đầu xe",
        "category": "Biển cấm",
        "description": "Báo cấm các loại xe rẽ trái đồng thời cấm quay đầu xe.",
        "penalty_details": "Phạt 400k-600k đồng"
    },
    "W-201b": {
        "model_class_id": "50",
        "name": "Chỗ ngoặt nguy hiểm vòng bên phải",
        "category": "Biển báo nguy hiểm",
        "description": "Báo trước sắp đến một chỗ ngoặt nguy hiểm vòng về bên phải.",
        "penalty_details": ""
    },
    "R-302b": {
        "model_class_id": "51",
        "name": "Chú ý chướng ngại vật – vòng tránh sang bên phải",
        "category": "Biển hiệu lệnh",
        "description": "Báo cho các loại xe phải vòng sang bên phải hoặc hai bên để tránh chướng ngại vật.",
        "penalty_details": ""
    },
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
