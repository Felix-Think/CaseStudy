from load import load_case
from save import save_case


# Save
# context, personas, skeleton = save_case("casestudy/cases/electric_shock_001")

# print("🏷️ Case:", context["case_id"])
# print("👥 Số nhân vật:", len(personas))
# print("🎬 Số sự kiện:", len(skeleton["canon_events"]))

# Load dữ liệu từ MongoDB
context, personas, skeleton = load_case("electric_shock_001", save_to_disk=False)

# --- Bây giờ bạn có thể xử lý trực tiếp ---
print("🏷️ Chủ đề:", context["topic"])
print("👥 Nhân vật:", [p["name"] for p in personas])
print("🎬 Sự kiện đầu:", skeleton["canon_events"][0]["title"])