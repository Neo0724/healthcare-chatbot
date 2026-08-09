from bson import ObjectId
from flask import jsonify

from app.utils.mongodb_client import get_database

db = get_database()
conversation_history = db["conversation_history"]
message = db["message"]


def delete_conversation_history(conversation_id):
    exist = conversation_history.find_one({"_id": ObjectId(conversation_id)})

    if not exist:
        return jsonify({"success": False, "error": "Not found"}), 400

    conversation_history.delete_one({"_id": exist["_id"]})

    message.delete_many({"conversation_id": exist["_id"]})

    return jsonify({"success": True}), 200
