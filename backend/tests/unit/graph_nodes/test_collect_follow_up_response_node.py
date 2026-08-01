from unittest.mock import MagicMock

import pytest

from app.graph_flow import collect_follow_up_response_node


@pytest.mark.parametrize(
    "user_input, expected",
    [
        (
            "Yes, I have mild fever and cough",
            "Yes, I have mild fever and cough",
        ),  # lower case
        (
            " Yes, I have mild fever and cough",
            "Yes, I have mild fever and cough",
        ),  # postfix space
        (
            "Yes, I have mild fever and cough ",
            "Yes, I have mild fever and cough",
        ),  # postfix space
        ("", ""),  # empty
    ],
)
def test_collect_follow_up_response_node(mocker, user_input, expected):

    # -------------------------
    # Arrange: fake assistant message
    # -------------------------
    mock_last_msg = MagicMock()
    mock_last_msg.content = "Do you have any fever or cough?"

    state = {"messages": [mock_last_msg], "user_messages": []}

    # -------------------------
    # Mock interrupt
    # -------------------------
    mock_interrupt = mocker.patch("app.graph_flow.interrupt", return_value=user_input)

    # -------------------------
    # Act
    # -------------------------
    result = collect_follow_up_response_node(state)

    # -------------------------
    # Assert
    # -------------------------

    # 1. interrupt called with correct prompt
    mock_interrupt.assert_called_once_with("Do you have any fever or cough?")

    # 2. trimmed response stored correctly
    assert result["user_messages"] == [expected]
