import bcrypt
from flask import jsonify
import jwt

from app.mongodb_client import get_database
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from app.schemas.auth import LoginRequest

load_dotenv()

SECRET = os.getenv("SECRET")

dbname = get_database()
user_collection = dbname["user"]


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

    return jsonify(
        {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    ), 200
