from unittest.mock import MagicMock
from types import SimpleNamespace

from app.graph_flow import process_and_diagnose_node


def test_process_and_diagnose_node(mocker):
    # -------------------------
    # Fake state
    # -------------------------
    mock_last_msg = MagicMock()
    mock_last_msg.content = "I have fever and cough"

    state = {"user_messages": [mock_last_msg], "messages": []}

    config = {"configurable": {"neo4j_driver": MagicMock()}}

    # -------------------------
    # Mock extracted entities
    # -------------------------
    mock_entities = SimpleNamespace(
        positive_symptoms=["fever", "cough"], negative_symptoms=["headache"]
    )

    mocker.patch("app.graph_flow.extract_symptoms", return_value=mock_entities)

    # -------------------------
    # Mock embeddings
    # -------------------------
    mock_embed = mocker.patch("app.graph_flow.embeddings_model")
    mock_embed.embed_query.side_effect = [
        [0.1, 0.2, 0.3],  # positive
        [0.4, 0.5, 0.6],  # negative
    ]

    # -------------------------
    # Mock DB function
    # -------------------------
    mock_get_diseases = mocker.patch(
        "app.graph_flow.get_possible_diseases",
        return_value=[
            {
                "disease_name": "flu",
                "post_score": 0.9,
                "symptom_node": ["fever", "cough"],
                "disease_id": "D1",
            }
        ],
    )

    # -------------------------
    # Mock LLM
    # -------------------------
    mock_llm = mocker.patch("app.graph_flow.llm")
    mock_llm.invoke.return_value = MagicMock(content="AI response")

    # -------------------------
    # Run node
    # -------------------------
    result = process_and_diagnose_node(state, config)

    # -------------------------
    # Assertions
    # -------------------------

    # 1. extraction called
    mocker.patch("app.graph_flow.extract_symptoms")
    # (optional: better to assert via spy, see note below)

    # 2. embeddings called correctly
    mock_embed.embed_query.assert_any_call("fever,cough")
    # mock_embed.embed_query.assert_any_call("headache")

    # 3. DB called correctly
    mock_get_diseases.assert_called_once_with(
        config["configurable"]["neo4j_driver"],
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    )

    # 4. output structure
    assert result["messages"][0].content == "AI response"
    assert result["extracted_positive_symptoms"] == ["fever", "cough"]
    # assert result["extracted_negative_symptoms"] == ["headatest_route_after_asking_disease_inft che"]
    assert result["initial_disease_ids"] == ["D1"]
