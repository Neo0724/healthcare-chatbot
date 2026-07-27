from bson import ObjectId
from flask import jsonify

from app.mongodb_client import get_database

db = get_database()
message_collection = db["message"]


def retrieve_conversation_message(conversation_id: str):
    messages = (
        message_collection.find(
            {"conversation_id": ObjectId(conversation_id)},
            {"_id": 1, "createdAt": 1, "type": 1, "content": 1},
        )
        .sort("createdAt", 1)
        .to_list()
    )

    for message in messages:
        message["_id"] = str(message["_id"])
        if "createdAt" in message:
            message["createdAt"] = message["createdAt"].isoformat()

    return jsonify({"success": True, "message": messages}), 200
