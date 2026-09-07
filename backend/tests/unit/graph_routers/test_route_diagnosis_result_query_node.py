import pytest

from app.graph_flow import route_diagnosis_result_query_node


@pytest.mark.parametrize(
    "user_input, expected",
    [
        ("yes", "request_disease_info"),
        ("YES", "request_disease_info"),       # uppercase
        ("yEs", "request_disease_info"),       # mixed case
        (" yes", "request_disease_info"),       # prefix space
        ("yes ", "request_disease_info"),       # postfix case

        ("no", "end_node"),
        ("NO", "end_node"),       # uppercase
        ("nO", "end_node"),       # mixed case
        (" no", "end_node"),       # prefix space
        ("no ", "end_node"),       # postfix case

        ("", "clarify_diagnosis_result_query"),       # empty case
    ],
)
def test_route_diagnosis_result_query_node(user_input: str, expected: str):
    state = {"diagnosis_result_query_choice": user_input}

    result = route_diagnosis_result_query_node(state)

    assert result == expected
