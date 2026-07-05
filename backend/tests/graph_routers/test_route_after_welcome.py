import pytest

from app.graph_flow import route_after_welcome


@pytest.mark.parametrize(
    "user_input, expected",
    [
        ("info", "request_disease_info"),
        ("symptom", "request_symptoms"),
    ],
)
def test_route_after_welcome(user_input: str, expected: str):
    state = {"routing_choice": user_input}

    result = route_after_welcome(state)

    assert result == expected
