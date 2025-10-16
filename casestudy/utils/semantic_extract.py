import json
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

BASE_DIR = Path(__file__).resolve().parents[1]

CASE_ID = "drowning_pool_001"
case_dir = BASE_DIR / "cases" / CASE_ID
logic_dir = case_dir / "logic_memory"
semantic_dir = case_dir / "semantic_memory"
scene_index_dir = semantic_dir / "scene_index"
persona_index_dir = semantic_dir / "persona_index"
policy_index_dir = semantic_dir / "policy_index"

semantic_dir.mkdir(parents=True, exist_ok=True)


def load_initial_context() -> Dict:
    context_path = logic_dir / "context.json"
    with context_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["initial_context"]


def load_personas() -> List[Dict]:
    personas_path = logic_dir / "personas.json"
    with personas_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("personas", [])


def normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            normalized[key] = value
        else:
            normalized[key] = json.dumps(value, ensure_ascii=False)
    return normalized


def build_scene_documents(context: Dict) -> List[Document]:
    scene = context["scene"]
    index_event = context["index_event"]
    resources = context["available_resources"]

    resource_text = ", ".join(
        resources.get("rescue", [])
        + resources.get("medical", [])
        + resources.get("human", [])
    )

    sections = [
        (
            "overview",
            f"Địa điểm: {scene['location']}. Thời tiết: {scene['weather']}. "
            f"Thời gian: {scene['time']}. Âm thanh: {scene['noise_level']}.",
        ),
        (
            "index_event",
            f"Sự kiện ban đầu: {index_event['summary']}. "
            f"Tình trạng hiện tại: {index_event['current_state']}.",
        ),
        ("resources", "Nguồn lực: " + resource_text),
        ("constraints", "Ràng buộc: " + ", ".join(context.get("constraints", []))),
    ]

    return [
        Document(
            page_content=text,
            metadata=normalize_metadata(
                {
                    "type": "scene",
                    "case_id": CASE_ID,
                    "section": section,
                }
            ),
        )
        for section, text in sections
    ]


def build_persona_documents(personas: List[Dict]) -> List[Document]:
    documents = []
    for persona in personas:
        emotions = list(
            filter(
                None,
                [
                    persona.get("emotion_init"),
                    *(persona.get("emotion_during", []) or []),
                    persona.get("emotion_end"),
                ],
            )
        )
        emotion_text = ", ".join(emotions) if emotions else "Chưa cập nhật"

        goal_text = persona.get("goal")
        if not goal_text:
            goal_text = ", ".join(persona.get("goals", [])) or "Chưa rõ"

        speech_text = persona.get("speech_pattern")
        if not speech_text:
            speech_text = ", ".join(persona.get("likely_lines", [])) or "Không có"

        trait_text = persona.get("personality")
        if not trait_text:
            raw_traits = persona.get("traits")
            trait_text = ", ".join(raw_traits) if isinstance(raw_traits, list) else raw_traits
        trait_text = trait_text or "Chưa rõ"

        page_content = (
            f"{persona.get('name', 'Ẩn danh')} ({persona.get('role', 'Chưa rõ')}) – "
            f"Tuổi: {persona.get('age', 'Chưa rõ')}. "
            f"Giới tính: {persona.get('gender', 'Chưa rõ')}. "
            f"Nền tảng: {persona.get('background', 'Chưa rõ')}. "
            f"Đặc điểm: {trait_text}. "
            f"Mục tiêu: {goal_text}. "
            f"Cảm xúc: {emotion_text}. "
            f"Mẫu lời nói: {speech_text}."
        )

        documents.append(
            Document(
                page_content=page_content,
                metadata=normalize_metadata(
                    {
                        "type": "persona",
                        "case_id": CASE_ID,
                        "persona_id": persona.get("id"),
                        "role": persona.get("role"),
                        "voice_tags": persona.get("voice_tags", []),
                        "emotion_tags": emotions,
                        "raw": persona,
                    }
                ),
            )
        )
    return documents


def build_policy_documents(context: Dict) -> List[Document]:
    policies = context.get("policies_safety_legal", [])
    documents = []
    for idx, policy in enumerate(policies):
        documents.append(
            Document(
                page_content=policy,
                metadata=normalize_metadata(
                    {
                        "type": "policy",
                        "case_id": CASE_ID,
                        "policy_id": f"policy_{idx + 1}",
                    }
                ),
            )
        )
    return documents


def build_indices() -> None:
    context = load_initial_context()
    personas = load_personas()

    scene_docs = build_scene_documents(context)
    persona_docs = build_persona_documents(personas)
    policy_docs = build_policy_documents(context)

    scene_index = Chroma.from_documents(
        scene_docs,
        embeddings,
        persist_directory=str(scene_index_dir),
    )
    persona_index = Chroma.from_documents(
        persona_docs,
        embeddings,
        persist_directory=str(persona_index_dir),
    )
    policy_index = Chroma.from_documents(
        policy_docs,
        embeddings,
        persist_directory=str(policy_index_dir),
    )

    scene_index.persist()
    persona_index.persist()
    policy_index.persist()


def load_indices():
    return (
        Chroma(persist_directory=str(scene_index_dir), embedding_function=embeddings),
        Chroma(persist_directory=str(persona_index_dir), embedding_function=embeddings),
        Chroma(persist_directory=str(policy_index_dir), embedding_function=embeddings),
    )


if __name__ == "__main__":
    #build_indices()

    scene_index, persona_index, policy_index = load_indices()

    print("\n--- Scene Query ---")
    for result in scene_index.similarity_search("Có bao nhiêu người tại hiện trường", k=2):
        print("→", result.page_content, "| metadata:", result.metadata)

    print("\n--- Persona Query ---")
    for result in persona_index.similarity_search("Ai là người nhà nạn nhân", k=1):
        print("→", result.page_content, "| metadata:", result.metadata)

    print("\n--- Policy Query ---")
    for result in policy_index.similarity_search("Tôn trọng quyền", k=4):
        print("→", result.page_content, "| metadata:", result.metadata)
