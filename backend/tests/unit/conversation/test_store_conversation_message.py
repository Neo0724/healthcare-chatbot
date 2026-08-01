from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.conversation.store_conversation_message import store_conversation_message


@pytest.mark.parametrize(
    "type",
    ["ai", "human"],
)
def test_store_conversation_message(client, mocker, type):
    mock_message_collection = mocker.patch(
        "app.conversation.store_conversation_message.message_collection"
    )
    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = "507f1f77bcf86cd799439011"

    mock_message_collection.insert_one.return_value = mock_insert_result

    inserted_id = store_conversation_message(
        "507f1f77bcf86cd799439011", "content", type
    )

    assert inserted_id == "507f1f77bcf86cd799439011"


def test_store_conversation_message_invalid_type(client, mocker):
    with pytest.raises(Exception):  # noqa: B017
        store_conversation_message("507f1f77bcf86cd799439011", "content", "none")
