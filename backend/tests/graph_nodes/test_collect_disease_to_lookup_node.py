import pytest
from unittest.mock import MagicMock

from app.graph_flow import collect_disease_to_lookup_node


@pytest.mark.parametrize(
    "user_choice, expected",
    [
        ("diabetes", "diabetes"),  # lower case
        (" diabetes", "diabetes"),  # postfix space
        ("diabetes ", "diabetes"),  # postfix space
        ("diabetes, asthma", "diabetes, asthma"),  # multiple
        ("diabetes, asthma, chest pain", "diabetes, asthma, chest pain"),  # multiple
    ],
)
def test_collect_disease_to_lookup_node(mocker, user_choice: str, expected: str):
    mock_last_message = MagicMock()
    mock_last_message.content = "What disease would you like to look up?"

    state = {"messages": [mock_last_message], "user_messages": []}

    mock_interrupt = mocker.patch("app.graph_flow.interrupt", return_value=user_choice)
    result = collect_disease_to_lookup_node(state)

    # 1. check LLM was called once
    mock_interrupt.assert_called_once_with(mock_last_message.content)

    # 2. check return value
    assert result["user_messages"] == [expected]
