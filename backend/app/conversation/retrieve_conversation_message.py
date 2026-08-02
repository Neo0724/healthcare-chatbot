from bson import ObjectId
from flask import jsonify

from app.utils.mongodb_client import get_database

db = get_database()
message_collection = db["message"]


def query_conversation_message(conversation_id):
    return (
        message_collection.find(
            {"conversation_id": ObjectId(conversation_id)},
            {"_id": 1, "createdAt": 1, "type": 1, "content": 1},
        )
        .sort("createdAt", 1)
        .to_list()
    )


def retrieve_conversation_message(conversation_id: str):
    messages = query_conversation_message(conversation_id)

    for message in messages:
        message["_id"] = str(message["_id"])
        if "createdAt" in message:
            message["createdAt"] = message["createdAt"].isoformat()

    return jsonify({"success": True, "message": messages}), 200
