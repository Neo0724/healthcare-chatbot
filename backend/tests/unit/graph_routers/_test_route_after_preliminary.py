import pytest

from app.graph_flow import route_after_preliminary


@pytest.mark.parametrize(
    "user_input, expected",
    [
        ("yes", "ask_follow_up"),
        ("YES", "ask_follow_up"),       # uppercase
        ("yEs", "ask_follow_up"),       # mixed case
        (" yes", "ask_follow_up"),       # prefix space
        ("yes ", "ask_follow_up"),       # postfix case

        ("no", "final_refined_diagnosis"),
        ("NO", "final_refined_diagnosis"),       # uppercase
        ("nO", "final_refined_diagnosis"),       # mixed case
        (" no", "final_refined_diagnosis"),       # prefix space
        ("no ", "final_refined_diagnosis"),       # postfix case

        ("", "final_refined_diagnosis"),       # empty case
    ],
)
def test_route_after_preliminary(user_input: str, expected: str):
    state = {"follow_up_agreement": user_input}

    result = route_after_preliminary(state)

    assert result == expected
