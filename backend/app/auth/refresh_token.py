from datetime import datetime, timedelta, timezone

from flask import jsonify
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("SECRET")


def refresh_token(refresh_token):
    try:
        decoded = jwt.decode(refresh_token, os.getenv("SECRET"), algorithms="HS256")

        user_id = decoded["sub"]
        username = decoded["username"]

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
