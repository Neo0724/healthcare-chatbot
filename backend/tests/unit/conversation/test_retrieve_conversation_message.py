from datetime import datetime


def test_retrieve_conversation_message(client, mocker):
    mock_request = mocker.patch("app.main.get_user_id")
    mock_request.return_value = "507f1f77bcf86cd799439011"

    mock_query_conversation_message = mocker.patch(
        "app.conversation.retrieve_conversation_message.query_conversation_message"
    )

    mock_query_conversation_message.return_value = [
        {"content": "a", "_id": "12345", "createdAt": datetime(2025, 7, 25, 12, 0, 0)},
    ]

    response = client.get("/get_conversation_message/12345")

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True
    assert "message" in body
    assert len(mock_query_conversation_message.return_value) == len(body["message"])
