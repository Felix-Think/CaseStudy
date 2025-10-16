# 🧠 KIẾN TRÚC 3 TẦNG TRÍ NHỚ CỦA CASESTUDY ENGINE
```text

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
 │                     🧱 TẦNG 1 – LOGIC MEMORY (STRUCTURED)                 │
 │ - Lưu: JSON / GraphStore                                                   │
 │ - Quản lý chuỗi Canon Events, các phase, preconditions, on_success / fail  │
 │ - Không embedding, truy xuất ID xác định                                   │
 │ - Dùng điều hướng flow LangGraph                                           │
 └────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                 🌐 TẦNG 2 – SEMANTIC MEMORY (NGỮ NGHĨA)                    │
 │ - Lưu: VectorDB (FAISS / Chroma / Milvus)                                  │
 │ - Gồm: Scene, Persona, Resource, Constraint, Policy…                       │
 │ - Cho phép truy vấn ngữ nghĩa (semantic search)                            │
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
 │ - Sinh: Scene narration, lời thoại, đánh giá hành động                     │
 │ - Xuất: Output ngắn (≤400 tokens) → cập nhật lại Runtime State             │
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
      │ 1️⃣ LOAD CASE DATA                           │
      │ - Load skeleton.json (logic)                │
      │ - Load scene_index, persona_index (semantic)│
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 2️⃣ RETRIEVE CONTEXT                         │
      │ - Query scene_index để lấy bối cảnh         │
      │ - Query persona_index để chọn nhân vật      │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 3️⃣ GENERATE SCENE CONTEXT                   │
      │ - LLM condense từ retrieved docs            │
      │ - Lưu scene_summary                         │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 4️⃣ SIMULATE DIALOGUE                        │
      │ - Nhận input học viên                       │
      │ - LLM tạo hội thoại (User ↔ Personas)       │
      │ - Update cảm xúc nhân vật                   │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 5️⃣ EVALUATE PHASE                           │
      │ - So sánh user_action với required_actions  │
      │ - Dựa trên success_criteria để đánh giá     │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 6️⃣ TRANSITION                               │
      │ - Lấy on_success / on_fail từ skeleton      │
      │ - Cập nhật current_event & phase            │
      └─────────────────────────────────────────────┘
                │
                ▼
      ┌─────────────────────────────────────────────┐
      │ 7️⃣ UPDATE STATE                             │
      │ - Lưu phase_summary, dialogue_history       │
      │ - Chuẩn bị vòng lặp mới                     │
      └─────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────────────────
...

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



# 🔧 HƯỚNG TRIỂN KHAI CỤ THỂ – SEMANTIC MEMORY (CHROMA + LLAMAINDEX)

🥇 Baseline: Duy trì persona_index (Chroma) cho retrieval nhanh & chính xác; mỗi nhân vật là Document có metadata, truy vấn bằng similarity_search().

🥈 Graph Persona: Thêm PersonaGraph trong LlamaIndex để mô tả mối quan hệ & trạng thái; tạo Graph Store (SimpleGraphStore/Neo4j), thiết lập các quan hệ KNOWS, TRUSTS, CONFLICTS_WITH, ...

🥉 Reasoning đa nhân vật: Dùng Query Engine để lý luận ngữ cảnh giữa nhiều nhân vật; engine trả về persona phù hợp qua graph embedding, node gọi query_engine.query().

🏆 Đồng bộ Runtime State: Kết hợp LlamaIndex reasoning với LangGraph state update; cập nhật state.active_personas, ghi cảm xúc & trust vào GraphState, cho phép nhân vật thay đổi cảm xúc theo thời gian.




                                     ┌────────────────────────────────────────────┐
                                     │             LOGIC MEMORY (Tầng 1)          │
                                     │  (skeleton.json)                           │
                                     │--------------------------------------------│
                                     │ • Danh sách Canon Events (CE1..CEn)        │
                                     │ • Mỗi CE: required_actions, success_criteria│
                                     │ • Định nghĩa on_success / on_fail           │
                                     └───────────────────────────────┬────────────┘
                                                                     │
                                                                     │ đọc cấu trúc logic
                                                                     ▼
                      ┌────────────────────────────────────────────────────────────────┐
                      │                SEMANTIC MEMORY (Tầng 2)                         │
                      │  (VectorDB Indexes: scene_index, persona_index, policy_index)   │
                      │----------------------------------------------------------------│
                      │ • scene_index: mô tả bối cảnh, nguồn lực, môi trường           │
                      │ • persona_index: dữ liệu nhân vật, tính cách, lời thoại mẫu    │
                      │ • policy_index: quy tắc, đạo đức, hướng dẫn hành động          │
                      └───────────────────────────────┬────────────────────────────────┘
                                                      │
                                                      │ truy vấn bằng embeddings
                                                      ▼
        ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
        │                        🧠 RUNTIME STATE (Tầng 3 - Active Memory)                             │
        │  (Được cập nhật liên tục bởi các Node trong LangGraph)                                      │
        │----------------------------------------------------------------------------------------------│
        │                                                                                              │
        │  IngressNode:              │  → Khởi tạo `case_id`, `current_event`                         │
        │  SemanticRetrievalNode:    │  → Lấy scene + personas từ tầng 2                              │
        │  PolicyCheckNode:          │  → Kiểm tra hành động người học theo policy                    │
        │  ActionEvaluatorNode:      │  → So khớp `user_action` với `required_actions` trong CE        │
        │  TransitionNode:           │  → Đổi `current_event` nếu pass/fail                            │
        │  StateUpdaterNode:         │  → Lưu `dialogue_history`, `user_action`                        │
        │  LLMResponderNode:         │  → Sinh phản hồi hội thoại (dựa trên state)                     │
        │  EgressNode:               │  → Lưu `runtime_state.json`                                     │
        │                                                                                              │
        └───────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                        │
                                                        │ serialize (dump)
                                                        ▼
                                 ┌────────────────────────────────────────────────────────┐
                                 │           runtime_state.json                            │
                                 │--------------------------------------------------------│
                                 │ case_id: drowning_pool_001                             │
                                 │ current_event: CE2                                     │
                                 │ scene_summary: "Hồ bơi công cộng, sàn trơn..."         │
                                 │ active_personas: {...}                                 │
                                 │ dialogue_history: [...]                                │
                                 │ event_summary: {"CE1": "pass"}                         │
                                 │ policy_flags: []                                       │
                                 └────────────────────────────────────────────────────────┘
                                 

#⚙️ 📊 GRAPH HOẠT ĐỘNG GIỮA CÁC NODE (VERSION 1 – LINEAR FLOW)

```text
┌────────────────────────────────────────────────────────────┐
│                        Ingress Node                        │
│────────────────────────────────────────────────────────────│
│  Input: case_id, start_event                               │
│  Action: khởi tạo hoặc load state cũ                       │
│  Output: RuntimeState(case_id, current_event)               │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────┐
│                 Semantic Retrieval Node                    │
│────────────────────────────────────────────────────────────│
│  Input: state.current_event, skeleton                      │
│  Action: query scene_index & persona_index                  │
│  Output: cập nhật → state.scene_summary, state.active_personas │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────┐
│                    Policy Check Node                       │
│────────────────────────────────────────────────────────────│
│  Input: state.user_action (nếu có)                         │
│  Action: query policy_index, phát hiện policy vi phạm       │
│  Output: cập nhật → state.policy_flags                     │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────┐
│                 Action Evaluator Node                      │
│────────────────────────────────────────────────────────────│
│  Input: state.user_action, skeleton.required_actions        │
│  Action: so sánh hành động với yêu cầu trong CE hiện tại    │
│  Output: cập nhật → state.event_summary[current_event]      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────┐
│                    Transition Node                         │
│────────────────────────────────────────────────────────────│
│  Input: state.event_summary, skeleton.on_success/on_fail    │
│  Action: quyết định event kế tiếp                          │
│  Output: cập nhật → state.current_event                     │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────┐
│                   State Updater Node                       │
│────────────────────────────────────────────────────────────│
│  Input: user_action, ai_reply, active_personas              │
│  Action: ghi lại hội thoại và cập nhật cảm xúc/trust        │
│  Output: cập nhật → state.dialogue_history, state.user_action │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────┐
│                    LLM Responder Node                      │
│────────────────────────────────────────────────────────────│
│  Input: scene_summary, active_personas, dialogue_history    │
│  Action: sinh phản hồi tự nhiên (AI → User)                 │
│  Output: ai_reply (in ra console hoặc UI)                   │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────┐
│                      Egress Node                           │
│────────────────────────────────────────────────────────────│
│  Input: RuntimeState                                       │
│  Action: lưu state ra file (runtime_state.json)            │
│  Output: checkpoint, log                                   │
└────────────────────────────────────────────────────────────┘
...