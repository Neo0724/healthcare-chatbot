from unittest.mock import MagicMock

from app.graph_flow import request_diagnosis_result_query_node


def test_request_diagnosis_result_query_node(mocker):
    state = {"messages": []}

    mock_response = MagicMock()
    mock_response.content = "Ask the user whether he or she would like to ask more question about the diagnosis results"

    mock_llm = mocker.patch("app.graph_flow.llm")

    mock_llm.invoke.return_value = mock_response
    result = request_diagnosis_result_query_node(state)

    # 1. check LLM was called once
    mock_llm.invoke.assert_called_once()

    _, kwargs = mock_llm.invoke.call_args

    assert kwargs["config"]["tags"] == ["user_message"]

    # 2. check return value
    assert result == {
        "messages": [mock_response]
    }