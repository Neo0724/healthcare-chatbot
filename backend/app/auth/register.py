import bcrypt
from flask import jsonify

from app.mongodb_client import get_database
from app.schemas.auth import RegisterRequest

dbname = get_database()
user_collection = dbname["user"]


def register_user(data: RegisterRequest):
    # Check existing user
    existing_user = user_collection.find_one({"username": data.username})

    if existing_user:
        return jsonify({"success": False, "error": "Username already exists"}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())

    # Create user document
    user = {"username": data.username, "password": hashed_password.decode("utf-8")}

    # Insert into database
    result = user_collection.insert_one(user)

    if not result.inserted_id:
        return jsonify({"success": False, "error": "Failed to create user"}), 500

    return jsonify({"success": True}), 201
