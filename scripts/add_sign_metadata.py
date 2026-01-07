import os
from pathlib import Path
import django

import sys
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "visionGT_BE.settings")
django.setup()

from traffic_signs.models import TrafficSign  # noqa: E402

# Extend this dict to add more curated metadata per class/model_class_id
SIGN_METADATA = {
    "DP-135": {
        "name": "Hết tất cả các lệnh cấm",
        "category": "Biển báo hết cấm",
        "description": "Báo hiệu đến đoạn đường mà nhiều biển báo cấm được đặt trước đó cùng hết hiệu lực."
    },
    "P-102": {
        "name": "Cấm đi ngược chiều",
        "category": "Cấm",
        "description": "Báo đường cấm tất cả các loại xe (cơ giới và thô sơ) đi vào theo chiều đặt biển, trừ các xe được ưu tiên theo quy định."
    },
    "P-103a": {
        "name": "Cấm xe ô tô",
        "category": "Cấm",
        "description": "Báo đường cấm tất cả các loại xe cơ giới, kể cả xe mô tô 3 bánh có thùng đi qua, trừ xe mô tô hai bánh, xe gắn máy và các xe được ưu tiên theo quy định."
    },
    "P-103b": {
        "name": "Cấm xe ô tô rẽ phải",
        "category": "Cấm",
        "description": "Báo cấm xe ô tô rẽ phải ở những nơi đường giao nhau, trừ các xe được ưu tiên theo quy định."
    },
    "P-103c": {
        "name": "Cấm xe ô tô rẽ trái",
        "category": "Cấm",
        "description": "Báo cấm xe ô tô rẽ trái ở những nơi đường giao nhau, trừ các xe được ưu tiên theo quy định."
    },
    "P-104": {
        "name": "Cấm xe mô tô",
        "category": "Cấm",
        "description": "Báo đường cấm tất cả các loại xe mô tô đi qua, trừ các xe được ưu tiên theo quy định. Biển không có giá trị cấm người dắt xe mô tô."
    },
    "P-106a": {
        "name": "Cấm xe ô tô tải",
        "category": "Cấm",
        "description": "Báo đường cấm các loại xe ô tô tải, trừ các xe được ưu tiên theo quy định. Biển này có hiệu lực cấm cả máy kéo và các xe máy chuyên dùng."
    },
    "P-106b": {
        "name": "Cấm xe ô tô tải có khối lượng chuyên chở lớn hơn giá trị ghi trên biển",
        "category": "Cấm",
        "description": "Báo đường cấm các loại xe ô tô tải có khối lượng chuyên chở (theo Giấy chứng nhận kiểm định an toàn kỹ thuật và bảo vệ môi trường phương tiện giao thông cơ giới đường bộ) vượt quá giá trị ghi trên biển, trừ các xe được ưu tiên theo quy định."
    },
    "P-107a": {
        "name": "Cấm xe ô tô khách",
        "category": "Cấm",
        "description": "Báo đường cấm ô tô chở khách đi qua trừ các xe ưu tiên theo quy định. Biển này không cấm xe buýt."
    },
    "P-112": {
        "name": "Cấm đi bộ",
        "category": "Cấm",
        "description": "Báo đường cấm người đi bộ qua lại để đảm bảo an toàn."
    },
    "P-115": {
        "name": "Hạn chế trọng lượng xe",
        "category": "Cấm",
        "description": "Báo đường cấm các loại xe (cơ giới và thô sơ), kể cả các xe được ưu tiên, có trọng lượng toàn bộ (cả xe và hàng) vượt quá trị số ghi trên biển đi qua."
    },
    "P-117": {
        "name": "Hạn chế chiều cao",
        "category": "Cấm",
        "description": "Báo cấm các xe (cơ giới và thô sơ) có chiều cao (tính cả xe và hàng hóa) vượt quá trị số ghi trên biển đi qua."
    },
    "P-123a": {
        "name": "Cấm rẽ trái",
        "category": "Cấm",
        "description": "Báo cấm các loại xe (cơ giới và thô sơ) rẽ trái ở những nơi đường giao nhau, trừ các xe được ưu tiên theo quy định."
    },
    "P-123b": {
        "name": "Cấm rẽ phải",
        "category": "Cấm",
        "description": "Báo cấm các loại xe (cơ giới và thô sơ) rẽ phải ở những nơi đường giao nhau, trừ các xe được ưu tiên theo quy định."
    },
    "P-124a": {
        "name": "Cấm quay đầu xe",
        "category": "Cấm",
        "description": "Báo cấm các loại xe (cơ giới và thô sơ) quay đầu xe theo kiểu chữ U, trừ các xe được ưu tiên theo quy định."
    },
    "P-124b": {
        "name": "Cấm ô tô quay đầu xe",
        "category": "Cấm",
        "description": "Báo cấm xe ô tô và xe mô tô 3 bánh quay đầu xe, trừ các xe được ưu tiên theo quy định."
    },
    "P-124c": {
        "name": "Cấm rẽ trái và quay đầu xe",
        "category": "Cấm",
        "description": "Báo cấm các loại xe rẽ trái đồng thời cấm quay đầu xe."
    },
    "P-127": {
        "name": "Tốc độ tối đa cho phép",
        "category": "Cấm",
        "description": "Báo tốc độ tối đa cho phép các xe cơ giới chạy. Biển có hiệu lực cấm các xe cơ giới chạy với tốc độ vượt quá trị số ghi trên biển."
    },
    "P-128": {
        "name": "Cấm sử dụng còi",
        "category": "Cấm",
        "description": "Báo cấm các loại xe cơ giới sử dụng còi."
    },
    "P-130": {
        "name": "Cấm dừng xe và đỗ xe",
        "category": "Cấm",
        "description": "Báo nơi cấm dừng xe và đỗ xe. Biển có hiệu lực cấm các loại xe cơ giới dừng và đỗ ở phía đường có đặt biển."
    },
    "P-131a": {
        "name": "Cấm đỗ xe",
        "category": "Cấm",
        "description": "Báo nơi cấm đỗ xe. Biển có hiệu lực cấm các loại xe cơ giới đỗ ở phía đường có đặt biển."
    },
    "P-137": {
        "name": "Cấm rẽ trái và rẽ phải",
        "category": "Cấm",
        "description": "Báo hiệu ở ngã đường phía trước cấm tất cả các loại xe rẽ trái hoặc rẽ phải."
    },
    "W-245a": {
        "name": "Đi chậm",
        "category": "Cảnh báo",
        "description": "Báo trước cho người tham gia giao thông biết sắp đến đoạn đường cần phải giảm tốc độ. Người lái xe cần phải đi chậm và chú ý quan sát."
    },
    "R-301c": {
        "name": "Hướng đi thẳng và rẽ phải phải theo",
        "category": "Hiệu lệnh",
        "description": "Báo hiệu các xe chỉ được đi thẳng và rẽ phải. Biển đặt ở sau nơi đường giao nhau."
    },
    "R-301d": {
        "name": "Hướng đi thẳng và rẽ trái phải theo",
        "category": "Hiệu lệnh",
        "description": "Báo hiệu các xe chỉ được đi thẳng và rẽ trái. Biển đặt ở sau nơi đường giao nhau."
    },
    "R-301e": {
        "name": "Hướng rẽ phải và rẽ trái phải theo",
        "category": "Hiệu lệnh",
        "description": "Báo hiệu các xe chỉ được rẽ phải và rẽ trái. Biển đặt ở sau nơi đường giao nhau."
    },
    "R-302a": {
        "name": "Hướng phải đi vòng chướng ngại vật (vòng sang bên trái)",
        "category": "Hiệu lệnh",
        "description": "Báo cho các loại xe (cơ giới và thô sơ) hướng đi để qua một chướng ngại vật, phải vòng sang bên trái."
    },
    "R-302b": {
        "name": "Hướng phải đi vòng chướng ngại vật (vòng sang hai bên)",
        "category": "Hiệu lệnh",
        "description": "Báo cho các loại xe (cơ giới và thô sơ) hướng đi để qua một chướng ngại vật, có thể vòng sang hai bên."
    },
    "R-303": {
        "name": "Nơi giao nhau chạy theo vòng xuyến",
        "category": "Hiệu lệnh",
        "description": "Báo cho các loại xe (thô sơ và cơ giới) phải chạy vòng theo đảo an toàn ở nơi đường giao nhau."
    },
    "R-407a": {
        "name": "Đường một chiều",
        "category": "Chỉ dẫn",
        "description": "Báo hiệu đường một chiều, chỉ cho phép các loại xe đi theo một chiều. Biển này đặt sau nơi đường giao nhau."
    },
    "R-409": {
        "name": "Chỗ quay xe",
        "category": "Chỉ dẫn",
        "description": "Báo hiệu vị trí được phép quay đầu xe."
    },
    "R-425": {
        "name": "Bệnh viện",
        "category": "Chỉ dẫn",
        "description": "Báo hiệu sắp đến bệnh viện. Người lái xe cần đi chậm, không bấm còi để giữ yên tĩnh."
    },
    "R-434": {
        "name": "Trạm dừng nghỉ",
        "category": "Chỉ dẫn",
        "description": "Báo hiệu sắp đến trạm dừng nghỉ. Biển cung cấp thông tin về các dịch vụ có tại trạm."
    },
    "S-509a": {
        "name": "Hướng đi",
        "category": "Phụ",
        "description": "Báo hướng đi và khoảng cách đến một địa điểm nào đó. Biển này thường được đặt dưới các biển chỉ dẫn."
    },
    "W-201a": {
        "name": "Chỗ ngoặt nguy hiểm vòng bên trái",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến một chỗ ngoặt nguy hiểm vòng về bên trái."
    },
    "W-201b": {
        "name": "Chỗ ngoặt nguy hiểm vòng bên phải",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến một chỗ ngoặt nguy hiểm vòng về bên phải."
    },
    "W-202a": {
        "name": "Nhiều chỗ ngoặt nguy hiểm liên tiếp (vòng bên trái trước)",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến nhiều chỗ ngoặt nguy hiểm liên tiếp, trong đó chỗ ngoặt đầu tiên vòng về bên trái."
    },
    "W-202b": {
        "name": "Nhiều chỗ ngoặt nguy hiểm liên tiếp (vòng bên phải trước)",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến nhiều chỗ ngoặt nguy hiểm liên tiếp, trong đó chỗ ngoặt đầu tiên vòng về bên phải."
    },
    "W-203b": {
        "name": "Đường bị hẹp về bên trái",
        "category": "Cảnh báo",
        "description": "Báo trước đoạn đường bị hẹp lại ở phía bên trái."
    },
    "W-203c": {
        "name": "Đường bị hẹp về bên phải",
        "category": "Cảnh báo",
        "description": "Báo trước đoạn đường bị hẹp lại ở phía bên phải."
    },
    "W-205a": {
        "name": "Đường giao nhau của các tuyến đường cùng cấp",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến nơi giao nhau của các tuyến đường cùng cấp (không có đường nào ưu tiên)."
    },
    "W-205b": {
        "name": "Đường giao nhau của các tuyến đường cùng cấp (giao nhau với đường từ bên phải và bên trái)",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến nơi giao nhau của các tuyến đường cùng cấp, có đường cắt ngang từ bên phải và bên trái."
    },
    "W-205d": {
        "name": "Đường giao nhau của các tuyến đường cùng cấp (giao nhau hình chữ T, đường chính đi thẳng và giao với đường phụ từ bên phải)",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến nơi giao nhau của các tuyến đường cùng cấp, giao nhau hình chữ T, đường chính đi thẳng và giao với đường phụ từ bên phải."
    },
    "W-207a": {
        "name": "Giao nhau với đường không ưu tiên (từ bên phải)",
        "category": "Cảnh báo",
        "description": "Đặt trên đường ưu tiên để báo trước sắp đến nơi giao nhau với đường không ưu tiên từ phía bên phải."
    },
    "W-207b": {
        "name": "Giao nhau với đường không ưu tiên (từ bên trái)",
        "category": "Cảnh báo",
        "description": "Đặt trên đường ưu tiên để báo trước sắp đến nơi giao nhau với đường không ưu tiên từ phía bên trái."
    },
    "W-207c": {
        "name": "Giao nhau với đường không ưu tiên (từ bên phải và bên trái)",
        "category": "Cảnh báo",
        "description": "Đặt trên đường ưu tiên để báo trước sắp đến nơi giao nhau với đường không ưu tiên từ cả hai phía."
    },
    "W-208": {
        "name": "Giao nhau với đường ưu tiên",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến nơi giao nhau với đường ưu tiên."
    },
    "W-209": {
        "name": "Giao nhau có tín hiệu đèn",
        "category": "Cảnh báo",
        "description": "Báo trước nơi giao nhau có sự điều khiển giao thông bằng tín hiệu đèn."
    },
    "W-210": {
        "name": "Giao nhau với đường sắt có rào chắn",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến chỗ giao nhau giữa đường bộ và đường sắt có rào chắn kín hay rào chắn nửa kín và có nhân viên ngành đường sắt điều khiển giao thông."
    },
    "W-219": {
        "name": "Dốc xuống nguy hiểm",
        "category": "Cảnh báo",
        "description": "Báo trước sắp tới dốc xuống nguy hiểm. Người điều khiển phương tiện phải chọn cách chạy phù hợp để đảm bảo an toàn."
    },
    "W-224": {
        "name": "Đường người đi bộ cắt ngang",
        "category": "Cảnh báo",
        "description": "Báo trước sắp tới phần đường dành cho người đi bộ sang đường. Các xe phải giảm tốc độ, nhường ưu tiên cho người đi bộ."
    },
    "W-225": {
        "name": "Trẻ em",
        "category": "Cảnh báo",
        "description": "Báo trước là gần đến đoạn đường thường có trẻ em đi ngang qua hoặc tụ tập trên đường như ở vườn trẻ, trường học."
    },
    "W-227": {
        "name": "Công trường",
        "category": "Cảnh báo",
        "description": "Báo trước gần tới đoạn đường đang tiến hành thi công, sửa chữa, nâng cấp."
    },
    "W-233": {
        "name": "Nguy hiểm khác",
        "category": "Cảnh báo",
        "description": "Báo trước những nguy hiểm có thể xảy ra mà chưa có loại biển báo nào trong hệ thống biển báo nguy hiểm và cảnh báo phù hợp để mô tả."
    },
    "W-235": {
        "name": "Đường đôi",
        "category": "Cảnh báo",
        "description": "Báo trước sắp đến đoạn đường có chiều đi và chiều về được phân chia bằng dải phân cách cứng."
    },
    "W-245a": {
        "name": "Đi chậm",
        "category": "Cảnh báo",
        "description": (
            "Biển báo nguy hiểm, nhắc người điều khiển giảm tốc độ khi sắp tới đoạn đường "
            "cần chú ý (công trường, đường trơn, dốc nguy hiểm...). Hình tam giác viền đỏ, nền vàng, "
            "chữ 'ĐI CHẬM' màu đen; đặt trước đoạn đường cần giảm tốc.")
    },
}


def run():
    created = 0
    updated = 0
    for sign_code, meta in SIGN_METADATA.items():
        obj, is_created = TrafficSign.objects.get_or_create(sign_Code=sign_code, defaults={
            "name": meta.get("name", sign_code),
            "category": meta.get("category", ""),
            "description": meta.get("description", ""),
            "model_class_id": meta.get("model_class_id"),
        })
        if is_created:
            created += 1
        else:
            # update existing fields
            obj.name = meta.get("name", obj.name)
            obj.category = meta.get("category", obj.category)
            obj.description = meta.get("description", obj.description)
            if meta.get("model_class_id"):
                obj.model_class_id = meta["model_class_id"]
            obj.save()
            updated += 1
    print(f"Metadata synced. Created: {created}, Updated: {updated}")


if __name__ == "__main__":
    run()
