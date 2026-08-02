from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from app.graph_flow import process_disease_info_node


def test_process_disease_info_node(
    mocker: MockerFixture,
):
    mock_last_message = MagicMock()
    mock_last_message.content = "I would like to look for diabetes"

    mock_response_message = MagicMock()
    mock_response_message.content = "Response by LLM"

    mock_embedding: MagicMock = mocker.patch("app.graph_flow.get_embedding_model")
    mock_model_instance = MagicMock()
    mock_embedding.return_value = mock_model_instance

    mock_model_instance.embed_query.return_value = [1, 1, 1]

    mock_extract_disease_name: MagicMock = mocker.patch(
        "app.graph_flow.extract_disease_names"
    )
    mock_extract_disease_name.return_value = ["diabetes"]

    mock_get_disease_information: MagicMock = mocker.patch(
        "app.graph_flow.get_diseases_information"
    )
    mock_get_disease_information.return_value = [
        {
            "disease_name": "diabetes",
            "score": 0.8,
            "definition_node": ["a", "b", "c"],
            "symptom_node": ["a", "b", "c"],
            "treatment_node": ["a", "b", "c"],
        }
    ]

    mock_reranker = mocker.patch("app.graph_flow.rerank_contexts")
    mock_reranker.return_value = ["b", "c", "a"]

    mock_llm: MagicMock = mocker.patch("app.graph_flow.llm")
    mock_llm.invoke.return_value = mock_response_message

    mock_driver = MagicMock()

    state = {"user_messages": [mock_last_message], "messages": []}
    config = {"configurable": {"neo4j_driver": mock_driver}}

    result = process_disease_info_node(state, config)

    # verify results
    mock_extract_disease_name.assert_called_once_with(mock_last_message)
    mock_get_disease_information.assert_called_once_with(
        mock_driver,
        mock_extract_disease_name.return_value,
        [mock_model_instance.embed_query.return_value],
    )
    mock_llm.invoke.assert_called_once()

    _, kwargs = mock_llm.invoke.call_args

    assert kwargs["config"]["tags"] == ["user_message"]

    for d in mock_extract_disease_name.return_value:
        mock_model_instance.embed_query.assert_called_with(d)

    # 2. check return value
    assert result["messages"] == [mock_response_message]
