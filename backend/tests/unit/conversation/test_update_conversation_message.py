from unittest.mock import MagicMock

from app.conversation.update_conversation_message import update_conversation_message


def test_update_conversation_message(client, mocker):
    mock_message_collection = mocker.patch(
        "app.conversation.update_conversation_message.message_collection"
    )

    mock_message_collection.find_one_and_update.return_value = None

    update_conversation_message("607f1f77bcf86cd799439011", new_content="new content")

    mock_message_collection.find_one_and_update.assert_called_once()
