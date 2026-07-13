from unittest.mock import MagicMock

from app.graph_flow import end_node


def test_end_node(mocker):
    state = {"messages": []}

    mock_response = MagicMock()
    mock_response.content = "Thank the user for using the app"

    mock_llm = mocker.patch("app.graph_flow.llm")

    mock_llm.invoke.return_value = mock_response
    result = end_node(state)

    # 1. check LLM was called once
    mock_llm.invoke.assert_called_once()

    _, kwargs = mock_llm.invoke.call_args

    assert kwargs["config"]["tags"] == ["user_message"]

    # 2. check return value
    assert result == {
        "messages": [mock_response]
    }