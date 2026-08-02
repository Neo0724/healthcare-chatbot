from bson import ObjectId


def test_delete_conversation_history_not_found(client, mocker):
    mock_conversation_history = mocker.patch(
        "app.conversation.delete_conversation_history.conversation_history"
    )
    mock_conversation_history.find_one.return_value = None

    response = client.delete("/delete_conversation/507f1f77bcf86cd799439011")

    body = response.get_json()

    assert response.status_code == 400
    assert body["success"] is False


def test_delete_conversation_history_valid(client, mocker):
    mock_conversation_history = mocker.patch(
        "app.conversation.delete_conversation_history.conversation_history"
    )
    mock_message = mocker.patch("app.conversation.delete_conversation_history.message")

    # Use a standard dictionary instead of MagicMock for the find_one return value
    mock_conversation_history.find_one.return_value = {
        "_id": ObjectId("507f1f77bcf86cd799439011")
    }

    response = client.delete("/delete_conversation/507f1f77bcf86cd799439011")
    body = response.get_json()

    mock_message.delete_one.assert_called_once()
    mock_conversation_history.delete_one.assert_called_once()

    conversation_args, _ = mock_conversation_history.delete_one.call_args
    message_args, _ = mock_message.delete_one.call_args

    assert response.status_code == 200
    assert body["success"] is True
    assert conversation_args[0]["_id"] == ObjectId("507f1f77bcf86cd799439011")
    assert message_args[0]["conversation_id"] == ObjectId("507f1f77bcf86cd799439011")