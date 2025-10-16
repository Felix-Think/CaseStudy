# 🧠 KIẾN TRÚC 3 TẦNG TRÍ NHỚ CỦA CASESTUDY ENGINE

                        ┌──────────────────────────────┐
                        │        INPUT (JSON)          │
                        │  case_id: drowning_pool_001  │
                        └──────────────┬───────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │                             │                             │
         ▼                             ▼                             ▼
 ┌───────────────────┐      ┌────────────────────┐       ┌─────────────────────┐
 │  skeleton.json    │      │  personas.json     │       │  context.json       │
 │ (Canon Events)    │      │ (Character Data)   │       │ (Scene / Policy /…) │
 └───────────────────┘      └────────────────────┘       └─────────────────────┘
         │                             │                             │
         │                             │                             │
         ▼                             ▼                             ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                     🧱 TẦNG 1 – LOGIC MEMORY (STRUCTURED)                   │
 │ - Lưu: JSON / GraphStore                                                   │
 │ - Quản lý chuỗi Canon Events, các phase, preconditions, on_success / fail  │
 │ - Không embedding, truy xuất ID xác định                                  │
 │ - Dùng điều hướng flow LangGraph                                          │
 └────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                 🌐 TẦNG 2 – SEMANTIC MEMORY (NGỮ NGHĨA)                    │
 │ - Lưu: VectorDB (FAISS / Chroma / Milvus)                                 │
 │ - Gồm: Scene, Persona, Resource, Constraint, Policy…                       │
 │ - Cho phép truy vấn ngữ nghĩa (semantic search)                           │
 │                                                                            │
 │  + scene_index       → Mô tả môi trường, thời tiết, nguồn lực              │
 │  + persona_index     → Nhân vật, tính cách, lời thoại                      │
 │  + policy_index      → Quy tắc, đạo đức, an toàn                           │
 │  + event_semantic_db → Success Criteria, required_actions (tuỳ chọn)       │
 └────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                  ⚙️ TẦNG 3 – RUNTIME STATE (BỘ NHỚ TẠM)                    │
 │ - Lưu trong RAM (GraphState / Cache JSON)                                  │
 │ - Cập nhật liên tục theo hành động học viên                                │
 │                                                                            │
 │  + case_id, current_event, phase      → từ skeleton                        │
 │  + scene_summary                      → từ LLM + VectorDB retrieval        │
 │  + active_personas (trạng thái)       → từ persona_index + runtime update  │
 │  + dialogue_history                   → log hội thoại                      │
 │  + phase_summary                      → kết quả từng phase                 │
 │  + user_action                        → hành động gần nhất                 │
 └────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                          🤖 LLM REASONER                                   │
 │ - Nhận: Logic (skeleton) + Semantic (VectorDB) + State hiện tại            │
 │ - Sinh: Scene narration, lời thoại, đánh giá hành động                    │
 │ - Xuất: Output ngắn (≤400 tokens) → cập nhật lại Runtime State            │
 └────────────────────────────────────────────────────────────────────────────┘


───────────────────────────────────────────────────────────────────────────────
         🔁 **LUỒNG XỬ LÝ TỔNG QUAN (PHASE LOOP)**
───────────────────────────────────────────────────────────────────────────────
┌────────────────────────────────────────────────────────────────────────────┐
│                           LANGGRAPH PHASE LOOP                             │
└────────────────────────────────────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 1️⃣ LOAD CASE DATA                          │
      │ - Load skeleton.json (logic)                │
      │ - Load scene_index, persona_index (semantic)│
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 2️⃣ RETRIEVE CONTEXT                        │
      │ - Query scene_index để lấy bối cảnh         │
      │ - Query persona_index để chọn nhân vật      │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 3️⃣ GENERATE SCENE CONTEXT                  │
      │ - LLM condense từ retrieved docs            │
      │ - Lưu scene_summary                         │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 4️⃣ SIMULATE DIALOGUE                       │
      │ - Nhận input học viên                       │
      │ - LLM tạo hội thoại (User ↔ Personas)       │
      │ - Update cảm xúc nhân vật                   │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 5️⃣ EVALUATE PHASE                          │
      │ - So sánh user_action với required_actions  │
      │ - Dựa trên success_criteria để đánh giá     │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 6️⃣ TRANSITION                              │
      │ - Lấy on_success / on_fail từ skeleton      │
      │ - Cập nhật current_event & phase            │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 7️⃣ UPDATE STATE                            │
      │ - Lưu phase_summary, dialogue_history       │
      │ - Chuẩn bị vòng lặp mới                    │
      └─────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────────────────

# 🧭 TƯ DUY KIẾN TRÚC


| Tầng                | Vai trò                                 | Lưu trữ                | Lý do                         |
| ------------------- | --------------------------------------- | ---------------------- | ----------------------------- |
| **Logic Memory**    | Quy định hành trình học                 | JSON / GraphStore      | Cần chính xác, không mơ hồ    |
| **Semantic Memory** | Cung cấp tri thức cho LLM hiểu thế giới | VectorDB               | Cần tìm theo nghĩa, không key |
| **Runtime State**   | Giữ trạng thái mô phỏng                 | LangGraph State / JSON | Cần cập nhật động, tạm thời   |

# 🧩 MỐI QUAN HỆ 3 TẦNG

                 ┌───────────────────────────────┐
                 │         LOGIC MEMORY          │
                 │  (skeleton.json / GraphStore) │
                 └─────────────┬─────────────────┘
                               │
                               ▼
                ┌───────────────────────────────┐
                │       SEMANTIC MEMORY         │
                │   (VectorDB: scene, persona)  │
                └─────────────┬─────────────────┘
                               │
                               ▼
                ┌───────────────────────────────┐
                │        RUNTIME STATE          │
                │ (LangGraph GraphState / JSON) │
                └─────────────┬─────────────────┘
                               │
                               ▼
                      🤖 LLM Reasoner
                  (Generate – Evaluate – Transition)


# ✅ Tóm tắt dễ hiểu

| Thành phần           | Tính chất             | Truy cập               | Cập nhật          | Vai trò                    |
| -------------------- | --------------------- | ---------------------- | ----------------- | -------------------------- |
| **Skeleton JSON**    | Tĩnh, cấu trúc logic  | Key lookup (`id`)      | Không thay đổi    | Điều khiển flow            |
| **VectorDB Indexes** | Ngữ nghĩa, dài, mô tả | Semantic search        | Ít thay đổi       | Cung cấp tri thức          |
| **LangGraph State**  | Động, phiên tạm       | Direct (Python object) | Cập nhật liên tục | Giữ tiến trình & hành động |
