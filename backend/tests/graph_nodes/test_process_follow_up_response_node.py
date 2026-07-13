from unittest.mock import MagicMock

import pytest

from app.graph_flow import process_follow_up_response_node


@pytest.mark.parametrize(
    "initial_positive, initial_negative, user_answer, extracted_positive, extracted_negative, expected_positive, expected_negative",
    [
        (
            ["cough"],
            ["headache"],
            "Yes",
            ["fever"],
            [],
            ["cough", "fever"],
            ["headache"],
        ),
        (
            ["cough"],
            ["headache"],
            "No",
            [],
            ["fever"],
            ["cough"],
            ["headache", "fever"],
        ),
    ],
)
def test_process_follow_up_response_node(
    mocker,
    initial_positive,
    initial_negative,
    user_answer,
    extracted_positive,
    extracted_negative,
    expected_positive,
    expected_negative,
):

    # -------------------------
    # Arrange state
    # -------------------------
    mock_question = MagicMock()
    mock_question.content = "Do you have fever?"

    mock_answer = MagicMock()
    mock_answer.content = user_answer

    state = {
        "messages": [mock_question],
        "user_messages": [mock_answer],
        "extracted_positive_symptoms": initial_positive,
        "extracted_negative_symptoms": initial_negative,
    }

    # -------------------------
    # Mock extractor output
    # -------------------------
    mock_extracted = MagicMock()
    mock_extracted.positive_symptoms = extracted_positive
    mock_extracted.negative_symptoms = extracted_negative

    mock_extract = mocker.patch(
        "app.graph_flow.extract_symptoms", return_value=mock_extracted
    )

    # -------------------------
    # Act
    # -------------------------
    result = process_follow_up_response_node(state)

    # -------------------------
    # Assert
    # -------------------------

    # 1. extractor called correctly
    mock_extract.assert_called_once_with(
        answer=user_answer, question="Do you have fever?"
    )

    # 2. positive symptoms merged correctly
    assert set(result["extracted_positive_symptoms"]) == set(expected_positive)
    # 3. negative symptoms merged correctly
    assert set(result["extracted_negative_symptoms"]) == set(expected_negative)
