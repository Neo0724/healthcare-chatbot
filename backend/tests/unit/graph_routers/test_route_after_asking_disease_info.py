import pytest

from app.graph_flow import route_after_asking_disease_info


@pytest.mark.parametrize(
    "user_input, expected",
    [
        ("yes", "request_disease_info"),
        ("YES", "request_disease_info"),  # uppercase
        ("yEs", "request_disease_info"),  # mixed case
        (" yes", "request_disease_info"),  # prefix space
        ("yes ", "request_disease_info"),  # postfix case
        ("no", "end_node"),
        ("NO", "end_node"),  # uppercase
        ("nO", "end_node"),  # mixed case
        (" no", "end_node"),  # prefix space
        ("no ", "end_node"),  # postfix case
        ("", "clarify_ask_more_disease_info"),  # empty case
    ],
)
def test_route_after_asking_disease_info(user_input: str, expected: str):
    state = {"ask_more_disease_info_choice": user_input}

    result = route_after_asking_disease_info(state)

    assert result == expected
