import os
from functools import wraps

import jwt
from flask import jsonify, request

SECRET = os.getenv("SECRET")


def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if os.getenv("ENVIRONMENT") == "testing" and request.path != "/test_jwt":
            return f(*args, **kwargs)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "missing token"}), 401

        try:
            token = auth_header.split(" ")[1]  # Bearer <token>

            payload = jwt.decode(token, SECRET, algorithms="HS256")

            request.user = payload  # attach user info to request

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "invalid token"}), 401

        return f(*args, **kwargs)

    return wrapper
