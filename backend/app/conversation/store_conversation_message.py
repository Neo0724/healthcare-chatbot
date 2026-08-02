from datetime import datetime, timedelta, timezone
from typing import Literal

from bson import ObjectId

from app.utils.mongodb_client import get_database

db = get_database()
message_collection = db["message"]


def store_conversation_message(
    conversation_id: str, content: str, type: Literal["ai", "human"]
):
    if type not in ["ai", "human"]:
        raise Exception("Invalid message type")  # noqa: TRY002

    created_message = message_collection.insert_one(
        {
            "conversation_id": ObjectId(conversation_id),
            "content": content,
            "type": type,
            "createdAt": datetime.now(timezone(timedelta(hours=8))),
        }
    )

    return str(created_message.inserted_id)
