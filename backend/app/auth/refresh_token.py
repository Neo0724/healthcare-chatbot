import os
from datetime import datetime, timedelta, timezone

import jwt
from bson import ObjectId
from dotenv import load_dotenv
from flask import jsonify

from app.mongodb_client import get_database

load_dotenv()

SECRET = os.getenv("SECRET")
db = get_database()
refresh_token_collection = db["issued_refresh_token"]


def refresh_token(refresh_token):
    try:
        decoded = jwt.decode(refresh_token, os.getenv("SECRET"), algorithms="HS256")

        user_id = decoded["sub"]
        username = decoded["username"]

        # Check if it is revoked or missing
        stored_token = refresh_token_collection.find_one(
            {"user_id": ObjectId(user_id), "token": str(refresh_token)}
        )

        if not stored_token:
            return jsonify({"success": False, "error": "token missing"}), 401

        if stored_token and stored_token["revoked"]:
            return jsonify({"success": False, "error": "token has been revoked"}), 401

        access_token_payload = {
            "sub": str(user_id),
            "username": username,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }

        refresh_token_payload = {
            "sub": str(user_id),
            "username": username,
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }

        new_access_token = jwt.encode(
            payload=access_token_payload, key=SECRET, algorithm="HS256"
        )

        new_refresh_token = jwt.encode(
            payload=refresh_token_payload, key=SECRET, algorithm="HS256"
        )

        refresh_token_collection.find_one_and_update(
            {"user_id": ObjectId(user_id), "token": str(refresh_token)},
            {"$set": {"revoked": True}},
        )

        refresh_token_collection.insert_one(
            {
                "user_id": ObjectId(user_id),
                "token": str(new_refresh_token),
                "revoked": False,
                "createdAt": datetime.now(),
            }
        )

        return jsonify(
            {
                "success": True,
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }
        ), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "error": "expired"}), 401

    except jwt.InvalidTokenError:
        return jsonify({"success": False, "error": "invalid token"}), 401
