import pytest
from unittest.mock import MagicMock

from app.graph_flow import collect_initial_symptoms_node


@pytest.mark.parametrize(
    "user_symptom, expected",
    [
        ("diabetes", "diabetes"),      # lower case
        (" diabetes", "diabetes"),      # postfix space 
        ("diabetes ", "diabetes"),      # postfix space 
        ("", ""),      # empty string 
    ]
)
def test_collect_initial_symptoms_node(mocker, user_symptom: str, expected: str):
    mock_last_message = MagicMock()
    mock_last_message.content = "Last message"

    state = {"messages": [mock_last_message], "user_messages": []}

    mock_interrupt = mocker.patch("app.graph_flow.interrupt", return_value=user_symptom)


    result = collect_initial_symptoms_node(state)
    
    # Verify function
    mock_interrupt.assert_called_once_with(mock_last_message.content)

    # 1. check return value
    assert result["user_messages"] == [expected]