from unittest.mock import MagicMock

from app.graph_flow import ask_follow_up_question_node


def test_ask_follow_up_question_node(mocker):

    # -------------------------
    # Fake state
    # -------------------------
    state = {
        "asked_questions_count": 2,
        "extracted_positive_symptoms": ["fever"],
        "extracted_negative_symptoms": ["cough"],
        "asked_questions": ["Do you have headache?"],
        "retrieved_disease_summary": [
            {
                "disease_name": "Diabetes",
                "match_score": 0.88,
                "disease_symptom_details": ["Diabetes is high blood sugar"],
            }
        ],
    }

    # -------------------------
    # Mock follow-up generator
    # -------------------------
    fake_follow_up = MagicMock()
    fake_follow_up.question = "Do you have sore throat?"
    fake_follow_up.reason = "Common flu symptom"

    mock_get_follow_up_questions = mocker.patch(
        "app.graph_flow.get_follow_up_questions", return_value=fake_follow_up
    )

    # -------------------------
    # Mock LLM
    # -------------------------
    fake_llm_response = MagicMock()
    fake_llm_response.content = "Follow-up question generated"

    mock_llm = mocker.patch("app.graph_flow.llm")
    mock_llm.invoke.return_value = fake_llm_response

    # -------------------------
    # Run node
    # -------------------------
    result = ask_follow_up_question_node(state)

    # -------------------------
    # Assertions
    # -------------------------

    # 1. follow-up generator called correctly
    mock_get_follow_up_questions.assert_called_once_with(
        [
            {
                "disease_name": "Diabetes",
                "match_score": 0.88,
                "disease_symptom_details": ["Diabetes is high blood sugar"],
            }
        ],
        ["fever"],
        ["cough"],
        ["Do you have headache?"],
    )

    # 2. LLM called once
    mock_llm.invoke.assert_called_once()

    # 3. check question tracking
    assert result["asked_questions_count"] == 3
    assert result["asked_questions"] == [
        "Do you have headache?",
        "Do you have sore throat?",
    ]

    # 4. response stored
    assert result["messages"] == [fake_llm_response]
