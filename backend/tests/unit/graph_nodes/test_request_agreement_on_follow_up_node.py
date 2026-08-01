from unittest.mock import MagicMock

from app.graph_flow import request_agreement_on_follow_up_node


def test_request_agreement_on_follow_up_node(mocker):

    # -------------------------
    # Fake LLM response
    # -------------------------
    fake_response = MagicMock()
    fake_response.content = "Do you want to answer follow-up questions?"

    # -------------------------
    # Mock LLM
    # -------------------------
    mock_llm = mocker.patch("app.graph_flow.llm")
    mock_llm.invoke.return_value = fake_response

    # -------------------------
    # Fake state
    # -------------------------
    state = {
        "messages": []
    }

    # -------------------------
    # Run node
    # -------------------------
    result = request_agreement_on_follow_up_node(state)

    # -------------------------
    # Assertions
    # -------------------------

    # 1. LLM called once
    mock_llm.invoke.assert_called_once()

    # 2. Check system prompt content
    _, kwargs = mock_llm.invoke.call_args

    # 3. Config tag check
    assert kwargs["config"]["tags"] == ["user_message"]

    # 4. Output structure
    assert result["messages"] == [fake_response]