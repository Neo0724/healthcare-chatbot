from unittest.mock import MagicMock

from app.graph_flow import final_refined_diagnosis_node


def test_final_refined_diagnosis_node(mocker):

    # -------------------------
    # Arrange state
    # -------------------------
    state = {
        "extracted_positive_symptoms": ["fever", "cough"],
        "extracted_negative_symptoms": ["headache"],
        "initial_disease_ids": ["D1", "D2"],
    }

    config = {"configurable": {"neo4j_driver": MagicMock()}}

    # -------------------------
    # Mock embeddings
    # -------------------------
    mock_embed = mocker.patch("app.graph_flow.get_embedding_model")
    mock_model_instance = MagicMock()
    mock_embed.return_value = mock_model_instance

    mock_model_instance.embed_query.side_effect = [
        [0.1, 0.2, 0.3],  # positive
        [0.4, 0.5, 0.6],  # negative
    ]

    # -------------------------
    # Mock DB function
    # -------------------------
    mock_narrow_down = mocker.patch(
        "app.graph_flow.narrow_down",
        return_value=[
            {
                "disease_name": "fever",
                "post_score": 0.92,
                "symptom_node": ["fever", "cough"],
            },
            {
                "disease_name": "cold",
                "post_score": 0.75,
                "symptom_node": ["cough"],
            },
        ],
    )

    # -------------------------
    # Mock LLM
    # -------------------------
    fake_llm_response = MagicMock()
    fake_llm_response.content = "Final diagnosis response"

    mock_llm = mocker.patch("app.graph_flow.llm")
    mock_llm.invoke.return_value = fake_llm_response

    # -------------------------
    # Act
    # -------------------------
    result = final_refined_diagnosis_node(state, config)

    # -------------------------
    # Assert
    # -------------------------

    # 1. embeddings called correctly
    mock_model_instance.embed_query.assert_any_call("fever,cough")
    # mock_embed.embed_query.assert_any_call("headache")

    # 2. DB query called correctly
    mock_narrow_down.assert_called_once_with(
        config["configurable"]["neo4j_driver"],
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        ["D1", "D2"],
    )

    # 3. LLM called once
    mock_llm.invoke.assert_called_once()

    # 4. return value
    assert result == {"messages": [fake_llm_response]}
