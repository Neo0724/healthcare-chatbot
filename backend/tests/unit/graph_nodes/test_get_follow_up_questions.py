from unittest.mock import MagicMock

from app.llm.get_follow_up_questions import get_follow_up_questions


def test_get_diseases_information(mocker):
    mock_classifier_chain = mocker.patch(
        "app.llm.get_follow_up_questions.classifier_chain"
    )

    mock_result = MagicMock()
    mock_result.question = "Question 1"
    mock_result.reason = "Reason 1"

    mock_classifier_chain.invoke.return_value = mock_result

    result = get_follow_up_questions(
        "input", ["headache"], ["fever"], ["Do you have fever?"]
    )

    assert result.question == "Question 1"
    assert result.reason == "Reason 1"
