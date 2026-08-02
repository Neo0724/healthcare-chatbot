from bson import ObjectId
from flask import jsonify

from app.utils.mongodb_client import get_database

db = get_database()
conversation_collection = db["conversation_history"]


def query_conversation_history(user_id):
    return (
        conversation_collection.find(
            {"user_id": ObjectId(user_id)},
            {"_id": 1, "createdAt": 1, "title": 1},
        )
        .sort("createdAt", -1)
        .to_list()
    )


def retrieve_conversation_history(user_id: str):
    conversations = query_conversation_history(user_id)

    for conversation in conversations:
        conversation["_id"] = str(conversation["_id"])
        if "createdAt" in conversation:
            conversation["createdAt"] = conversation["createdAt"].isoformat()

    return jsonify({"success": True, "conversation_history": conversations}), 200
