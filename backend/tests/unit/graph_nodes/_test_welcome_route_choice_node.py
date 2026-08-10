from unittest.mock import MagicMock

import pytest

from app.graph_flow import welcome_route_choice_node


@pytest.mark.parametrize(
    "user_choice, expected",
    [
        ("info", "info"),      # lower case
        ("INFO", "info"),      # upper case
        ("InFo", "info"),      # mixed case
        (" info", "info"),      # postfix space 
        ("info ", "info"),      # postfix space 
        ("", ""),      # empty string 
    ]
)
def test_welcome_route_choice_node(mocker, user_choice: str, expected: str):
    mock_response = MagicMock()
    mock_response.content = "Choose find disease info or preliminary diagnosis"
    
    state = {
        "messages": [mock_response],
        "routing_choice": "",
    }

    # Mock LangGraph interrupt()
    mock_interrupt = mocker.patch("app.graph_flow.interrupt", return_value=user_choice)
    result = welcome_route_choice_node(state)

    # Check interrupt was called with AI message
    mock_interrupt.assert_called_once_with(
        "Choose find disease info or preliminary diagnosis"
    )

    # Check state update
    assert result["routing_choice"] == expected
