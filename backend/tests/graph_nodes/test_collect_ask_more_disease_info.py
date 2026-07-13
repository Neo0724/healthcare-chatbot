from unittest.mock import MagicMock

import pytest

from app.graph_flow import collect_ask_more_disease_info


@pytest.mark.parametrize(
    "user_input, expected",
    [
        ("yes", "yes"),
        (" yes", "yes"),  # prefix space
        ("yes ", "yes"),  # postfix space
        ("", ""),  # empty 
    ],
)
def test_collect_ask_more_disease_info(mocker, user_input: str, expected: str):

    # -------------------------
    # Fake last assistant message
    # -------------------------
    mock_last_msg = MagicMock()
    mock_last_msg.content = "Do you want to ask more disease information?"

    state = {"messages": [mock_last_msg], "user_messages": []}

    # -------------------------
    # Mock interrupt
    # -------------------------
    mock_interrupt = mocker.patch("app.graph_flow.interrupt", return_value=user_input)

    # -------------------------
    # Run node
    # -------------------------
    result = collect_ask_more_disease_info(state)

    # -------------------------
    # Assertions
    # -------------------------

    # 1. interrupt called with last message content
    mock_interrupt.assert_called_once_with(mock_last_msg.content)

    # 2. user input stored correctly (trimmed)
    assert result["ask_more_disease_info_choice"] == expected

    # 3. user_messages updated correctly
    assert result["user_messages"] == [expected]
