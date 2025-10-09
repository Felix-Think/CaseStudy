                          ┌──────────────────────────────┐
                          │        INPUT (JSON)          │
                          │  case_id: drowning_pool_001  │
                          └──────────────┬───────────────┘
                                         │
                   ┌─────────────────────┼─────────────────────┐
                   │                     │                     │
                   ▼                     ▼                     ▼
       ┌─────────────────┐     ┌────────────────────┐  ┌──────────────────────┐
       │ skeleton.json   │     │ personas.json      │  │ context.json         │
       │ (Canon Events)  │     │ (Character Data)   │  │ (Scene, Policy, ...) │
       └─────────────────┘     └────────────────────┘  └──────────────────────┘
                   │                     │                     │
                   │                     │                     │
                   ▼                     ▼                     ▼
───────────────────────────────────────────────────────────────────────────────
         🧱 **TẦNG 1 – LOGIC MEMORY (CẤU TRÚC DETERMINISTIC)**
───────────────────────────────────────────────────────────────────────────────
- Lưu ở dạng: JSON / GraphStore  
- Quản lý các "Canon Events" – chuỗi logic học tập  
- Quy định: phase, preconditions, required_actions, on_success / on_fail  
- Không có embedding – chỉ truy xuất theo ID  
- Dùng để điều hướng flow trong LangGraph

👉 **Ví dụ:**  
`CE1_DANH_GIA_AN_TOAN → CE2_KICH_HOAT_CAP_CUU`  
Nếu user đạt tiêu chí thì chuyển node logic.

───────────────────────────────────────────────────────────────────────────────
         🌐 **TẦNG 2 – SEMANTIC MEMORY (TRÍ NHỚ NGỮ NGHĨA)**
───────────────────────────────────────────────────────────────────────────────
- Lưu ở dạng: VectorDB (FAISS / Chroma / Milvus)  
- Gồm: Scene, Persona, Resource, Constraint, Policy, Success Criteria (rút gọn)  
- Mỗi tài liệu = 1 Document có embedding  
- Cho phép truy vấn theo *ngữ nghĩa* ("ai có thể giúp", "rủi ro hiện trường")  

| Loại Index | Nội dung | Dùng cho |
|-------------|-----------|-----------|
| `scene_index` | Mô tả môi trường, thời tiết, tiếng ồn, nguồn lực | Sinh “bối cảnh” |
| `persona_index` | Nhân vật, vai trò, tính cách, lời thoại mẫu | Sinh hội thoại |
| `policy_index` | Quy định hành động, đạo đức, an toàn | Đánh giá hành động |
| `event_semantic_index` *(tuỳ chọn)* | Mô tả hành động/tiêu chí trong canon event | Trợ giúp evaluate |

→ **VectorDB** là “bộ nhớ hiểu biết” mà LLM có thể hỏi lại khi cần biết **nội dung mô phỏng**,  
chứ không chứa logic flow.

───────────────────────────────────────────────────────────────────────────────
         ⚙️ **TẦNG 3 – RUNTIME STATE (BỘ NHỚ TẠM / HOẠT ĐỘNG)**
───────────────────────────────────────────────────────────────────────────────
- Lưu trong RAM (LangGraph `GraphState`) hoặc cache JSON  
- Cập nhật theo thời gian thực khi người học tương tác  
- Gồm cả dữ liệu “tạm” và “trạng thái động”:

| Trường | Mô tả | Nguồn |
|---------|--------|--------|
| `case_id`, `current_event`, `current_phase` | xác định vị trí trong flow | Skeleton |
| `scene_summary` | tóm tắt ngắn gọn hiện trường | VectorDB + LLM |
| `active_personas` | danh sách nhân vật đang hoạt động + trạng thái cảm xúc | PersonaIndex + runtime |
| `dialogue_history` | log hội thoại (user ↔ AI) | runtime |
| `phase_summary` | kết quả của từng phase (đạt/chưa đạt) | Evaluate Node |
| `user_action` | hành động gần nhất của học viên | runtime |

→ Đây là nơi **LangGraph điều phối thực tế** và **LLM reasoning** hoạt động.

───────────────────────────────────────────────────────────────────────────────
         🤖 **LLM REASONER**
───────────────────────────────────────────────────────────────────────────────
- Nhận input:  
  (1) Logic từ Skeleton JSON  
  (2) Context semantic từ VectorDB  
  (3) Trạng thái hiện tại từ State  
- Thực hiện:  
  - Viết scene narration  
  - Sinh lời thoại nhân vật  
  - Đánh giá hành động học viên  
- Trả output ngắn gọn (≤400 token) → update State

───────────────────────────────────────────────────────────────────────────────
         🔁 **LUỒNG XỬ LÝ TỔNG QUAN (PHASE LOOP)**
───────────────────────────────────────────────────────────────────────────────
1️⃣ **Load case data**  
 → load skeleton.json (logic)  
 → load scene_index & persona_index (semantic)

2️⃣ **Retrieve Scene & Personas**  
 → query VectorDB theo phase_id

3️⃣ **Generate Scene Context**  
 → LLM condense từ retrieved docs → scene_summary

4️⃣ **User Action / Dialogue**  
 → user input → LLM + state.active_personas → simulate conversation

5️⃣ **Evaluate Phase**  
 → so khớp user_action với required_actions trong skeleton  
 → chấm điểm bằng success_criteria

6️⃣ **Transition**  
 → lấy `on_success` hoặc `on_fail` từ skeleton  
 → cập nhật `current_event` và `phase`

7️⃣ **Repeat** đến khi hết canon event.

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
