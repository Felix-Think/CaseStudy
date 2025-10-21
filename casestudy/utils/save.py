# ==============================================
# 📦 save.py — Lưu dữ liệu CaseStudy vào MongoDB
# ==============================================
import os
import sys
import json
from pymongo import MongoClient

# -------------------------
# ⚙️ Cấu hình MongoDB
# -------------------------
MONGO_URI = "mongodb+srv://nvt120205:thang1202@thangnguyen.8aiscbh.mongodb.net/"
DB_NAME = "case_study_db"


# -------------------------
# 💾 Hàm lưu case
# -------------------------
def save_case(case_folder):
    """
    Lưu dữ liệu từ thư mục CaseStudyData/<case_folder> vào MongoDB.
    Trả về tuple: (context, personas, skeleton)
    """
    # Xác định đường dẫn thư mục case
    if os.path.isdir("CaseStudyData"):
        base_dir = os.path.join("CaseStudyData", case_folder)
    else:
        base_dir = case_folder  # nếu không có thư mục bao ngoài

    if not os.path.exists(base_dir):
        print(f"❌ Không tìm thấy thư mục: {base_dir}")
        return None, None, None

    # Kết nối MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Đọc context.json
    with open(os.path.join(base_dir, "context.json"), "r", encoding="utf-8") as f:
        context = json.load(f)
    case_id = context.get("case_id", case_folder)

    # Xóa dữ liệu cũ trước khi ghi
    db.contexts.delete_many({"case_id": case_id})
    db.personas.delete_many({"case_id": case_id})
    db.skeletons.delete_many({"case_id": case_id})

    # Đọc personas.json
    personas_path = os.path.join(base_dir, "personas.json")
    with open(personas_path, "r", encoding="utf-8") as f:
        personas = json.load(f)["personas"]
        for p in personas:
            p["case_id"] = case_id

    # Đọc skeleton.json
    skeleton_path = os.path.join(base_dir, "skeleton.json")
    with open(skeleton_path, "r", encoding="utf-8") as f:
        skeleton = json.load(f)
    skeleton["case_id"] = case_id

    # Ghi vào MongoDB
    db.contexts.insert_one(context)
    db.personas.insert_many(personas)
    db.skeletons.insert_one(skeleton)

    print(f"✅ Đã lưu case '{case_id}' vào MongoDB thành công!")
    return context, personas, skeleton


# -------------------------
# 🚀 Chạy từ terminal
# -------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❗Cách dùng: python save.py <tên_folder_case>")
        print("👉 Ví dụ: python save.py electric_shock_001")
    else:
        case_folder = sys.argv[1]
        save_case(case_folder)
