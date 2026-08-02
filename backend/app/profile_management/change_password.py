import bcrypt
from bson import ObjectId
from flask import jsonify

from app.utils.mongodb_client import get_database

db = get_database()

user_collection = db["user"]


def change_password(current_password, new_password, user_id):
    user = user_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"success": False, "error": "User not found"}), 400

    matched = bcrypt.checkpw(
        current_password.encode("utf-8"), user["password"].encode("utf-8")
    )

    if not matched:
        return jsonify({"success": False, "error": "Password not matched"}), 400

    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

    user_collection.find_one_and_update(
        {
            "_id": ObjectId(user_id),
        },
        {"$set": {"password": hashed_password.decode()}},
    )

    return jsonify({"success": True}), 200
