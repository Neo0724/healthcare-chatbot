from datetime import datetime, timedelta, timezone

from bson import ObjectId
from flask import jsonify

from app.llm.extract_conversation_title import extract_conversation_title
from app.utils.mongodb_client import get_database

db = get_database()
conversation_collection = db["conversation_history"]
message_collection = db["message"]


def store_conversation_history(user_id: str, user_query: str):
    conversation_title = extract_conversation_title(user_query)
    created_conversation = conversation_collection.insert_one(
        {
            "user_id": ObjectId(user_id),
            "title": str(conversation_title),
            "createdAt": datetime.now(timezone(timedelta(hours=8))),
        }
    )

    message_collection.insert_one(
        {
            "conversation_id": created_conversation.inserted_id,
            "content": user_query,
            "type": "human",
            "createdAt": datetime.now(timezone(timedelta(hours=8))),
        }
    )

    return jsonify(
        {"success": True, "conversation_id": str(created_conversation.inserted_id)}
    ), 200
