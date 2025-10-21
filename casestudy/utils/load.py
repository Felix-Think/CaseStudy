import os
import sys
import json
from pathlib import Path

import certifi
from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb+srv://nvt120205:thang1202@thangnguyen.8aiscbh.mongodb.net/"
DB_NAME = "case_study_db"

CASESTUDY_ROOT = Path(__file__).resolve().parents[1]
LOCAL_CASES_DIR = CASESTUDY_ROOT / "cases"


def load_case(case_id, save_to_disk=True):
    """
    Trả về dữ liệu CaseStudy dạng dict:
    {
      'context': {...},
      'personas': [...],
      'skeleton': {...}
    }

    Nếu save_to_disk=True → đồng thời ghi file JSON ra thư mục local.
    """
    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where(),
        )
        db = client[DB_NAME]

        context = db.contexts.find_one({"case_id": case_id})
        personas = list(db.personas.find({"case_id": case_id}))
        skeleton = db.skeletons.find_one({"case_id": case_id})
    except PyMongoError as exc:
        print(f"⚠️ Không thể kết nối MongoDB ({exc}). Đọc dữ liệu local.")
        return _load_local_case(case_id, save_to_disk=save_to_disk)

    if not (context or personas or skeleton):
        print(f"❌ Không tìm thấy dữ liệu cho case_id: {case_id}")
        return _load_local_case(case_id, save_to_disk=save_to_disk)

    # Xóa _id của MongoDB
    if context: context.pop("_id", None)
    if skeleton: skeleton.pop("_id", None)
    for p in personas: p.pop("_id", None)

    # Ghi ra file nếu cần
    if save_to_disk:
        base_dir = _persist_case_to_disk(case_id, context, personas, skeleton)
        print(f"💾 Đã lưu dữ liệu case '{case_id}' vào thư mục {base_dir}")

    return context, personas, skeleton


def _load_local_case(case_id, save_to_disk=True):
    logic_dir = LOCAL_CASES_DIR / case_id / "logic_memory"
    if not logic_dir.exists():
        print(f"❌ Không tìm thấy dữ liệu local cho case_id: {case_id}")
        return None, None, None

    try:
        with (logic_dir / "context.json").open("r", encoding="utf-8") as f:
            context = json.load(f)
        with (logic_dir / "personas.json").open("r", encoding="utf-8") as f:
            personas_payload = json.load(f)
            personas = personas_payload.get("personas", [])
        with (logic_dir / "skeleton.json").open("r", encoding="utf-8") as f:
            skeleton = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"❌ Lỗi đọc dữ liệu local cho case_id {case_id}: {exc}")
        return None, None, None

    if save_to_disk:
        base_dir = _persist_case_to_disk(case_id, context, personas, skeleton)
        print(f"💾 Đã lưu dữ liệu case '{case_id}' từ local vào thư mục {base_dir}")

    return context, personas, skeleton


def _persist_case_to_disk(case_id, context, personas, skeleton):
    base_dir = os.path.join("CaseStudyData", case_id)
    os.makedirs(base_dir, exist_ok=True)
    with open(os.path.join(base_dir, "context.json"), "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=2)
    with open(os.path.join(base_dir, "personas.json"), "w", encoding="utf-8") as f:
        json.dump({"personas": personas}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(base_dir, "skeleton.json"), "w", encoding="utf-8") as f:
        json.dump(skeleton, f, ensure_ascii=False, indent=2)
    return base_dir


def load_case_from_local(case_id: str):
    """
    Hàm tiện ích public để lấy dữ liệu case từ thư mục local mà không ghi ra disk.
    """
    return _load_local_case(case_id, save_to_disk=False)


# -------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❗Cách dùng: python load.py <case_id>")
        print("👉 Ví dụ: python load.py electric_shock_001")
    else:
        case_id = sys.argv[1]
        ctx, pers, skel = load_case(case_id, save_to_disk=True)
        print(f"🎯 Đã load dữ liệu: {len(pers)} personas, {len(skel['canon_events'])} events.")
