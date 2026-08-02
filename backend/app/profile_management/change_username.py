from bson import ObjectId
from flask import jsonify

from app.utils.mongodb_client import get_database

db = get_database()
user_collection = db["user"]


def change_username(new_username, user_id):
    user = user_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"success": False, "error": "User not found"}), 400

    existing_user = user_collection.find_one({"username": new_username})

    if existing_user:
        return jsonify({"success": False, "error": "Username existed"}), 400

    user_collection.find_one_and_update(
        {"_id": ObjectId(user_id)}, {"$set": {"username": new_username}}
    )

    return jsonify({"success": True}), 200
