import pytest

from app.graph_flow import route_follow_up_loop


@pytest.mark.parametrize(
    "user_input, expected",
    [
        (0, "ask_follow_up"),
        (4, "ask_follow_up"),
        (5, "final_refined_diagnosis"),
        (6, "final_refined_diagnosis"),
    ],
)
def test_route_after_preliminary(user_input: int, expected: str):
    state = {"asked_questions_count": user_input}

    result = route_follow_up_loop(state)

    assert result == expected
