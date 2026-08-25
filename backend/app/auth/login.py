import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from flask import jsonify

from app.schemas.auth import LoginRequest
from app.utils.mongodb_client import get_database

load_dotenv()

SECRET = os.getenv("SECRET")

db = get_database()
user_collection = db["user"]
refresh_token_collection = db["issued_refresh_token"]


def login_user(data: LoginRequest):
    username = data.username
    password = data.password

    user = user_collection.find_one({"username": username})

    if not user:
        return jsonify(
            {
                "success": False,
                "error": "Username not found",
            }
        ), 404

    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify(
            {
                "success": False,
                "error": "Password incorrect",
            }
        ), 401

    access_token_payload = {
        "sub": str(user["_id"]),
        "username": user["username"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    refresh_token_payload = {
        "sub": str(user["_id"]),
        "username": user["username"],
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }

    access_token = jwt.encode(
        payload=access_token_payload, key=SECRET, algorithm="HS256"
    )

    refresh_token = jwt.encode(
        payload=refresh_token_payload, key=SECRET, algorithm="HS256"
    )

    refresh_token_collection.insert_one(
        {
            "token": refresh_token,
            "user_id": user["_id"],
            "revoked": False,
            "createdAt": datetime.now(timezone(timedelta(hours=8))),
        }
    )

    return jsonify(
        {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    ), 200
