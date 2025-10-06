from agent.chain.generate_scene import generate_scene



input_state = {
    "objective_learning": "Hiểu và áp dụng các khái niệm cơ bản về lập trình Python.",
    "initial_context": "Học sinh đã có kiến thức cơ bản về lập trình.",
    "persona": {
        "name": "Cô Lan",
        "role": "Giáo viên",
        "traits": ["nhiệt huyết", "kiên nhẫn", "khuyến khích"],
        "speaking_style": "thân thiện và dễ hiểu",
    },
}
def test_generate_scene(input_state) -> None:
    result_state = generate_scene(input_state)
    assert "generated_scene" in result_state
    print("Kết quả tạo tình huống:")
    print(result_state)


test_generate_scene(input_state)