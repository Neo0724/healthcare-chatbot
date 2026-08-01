from datetime import datetime
from unittest.mock import MagicMock

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

    mock_conversation_history_find_result = MagicMock()
    mock_conversation_history_find_result._id = ObjectId("507f1f77bcf86cd799439011")

    mock_conversation_history.find_one.return_value = (
        mock_conversation_history_find_result
    )

    response = client.delete("/delete_conversation/507f1f77bcf86cd799439011")

    body = response.get_json()

    args, _ = mock_conversation_history.delete_one.call_args

    assert response.status_code == 200
    assert body["success"] is True
    assert args[0]["_id"] == ObjectId("507f1f77bcf86cd799439011")
