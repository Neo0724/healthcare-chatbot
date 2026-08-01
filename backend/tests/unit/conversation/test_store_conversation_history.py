from unittest.mock import MagicMock


def test_store_conversation_history(client, mocker):
    mock_request = mocker.patch("app.main.get_user_id")
    mock_request.return_value = "507f1f77bcf86cd799439011"

    mock_extract_conversation_title = mocker.patch(
        "app.conversation.store_conversation_history.extract_conversation_title"
    )
    mock_extract_conversation_title.return_value = "Title 1"

    mock_conversation_collection = mocker.patch(
        "app.conversation.store_conversation_history.conversation_collection"
    )
    mock_created_conversation_result = MagicMock()
    mock_created_conversation_result.inserted_id = "607f1f77bcf86cd799439011"
    mock_conversation_collection.insert_one.return_value = (
        mock_created_conversation_result
    )

    mock_message_collection = mocker.patch(
        "app.conversation.store_conversation_history.message_collection"
    )
    mock_created_message_result = MagicMock()
    mock_created_message_result.inserted_id = "507f1f77bcf86cd799439011"

    mock_message_collection.insert_one.return_value = mock_created_message_result

    payload = {"user_input": "Hello"}

    response = client.post("/create_conversation", json=payload)

    body = response.get_json()

    args, _ = mock_message_collection.insert_one.call_args
    inserted_doc = args[0]

    assert inserted_doc["conversation_id"] == "607f1f77bcf86cd799439011"
    assert response.status_code == 200
    assert body["success"] is True
    assert body["conversation_id"] == "607f1f77bcf86cd799439011"
