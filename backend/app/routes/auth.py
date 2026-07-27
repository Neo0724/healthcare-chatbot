import os

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.auth.login import login_user
from app.auth.logout import logout_user
from app.auth.refresh_token import refresh_token
from app.auth.register import register_user
from app.schemas.auth import LoginRequest, RegisterRequest

SECRET = os.getenv("SECRET")


# Create the blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        # Parse and validate data against the Pydantic schema
        data = LoginRequest(**request.get_json())

        return login_user(data)

    except ValidationError as e:
        # Returns clear, structured errors to the client
        response = {"success": False, "error": e.errors()}
        return jsonify(response), 400


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        # Parse and validate data against the Pydantic schema
        data = RegisterRequest(**request.get_json())

        return register_user(data)

    except ValidationError as e:
        # Returns clear, structured errors to the client
        response = {"success": False, "error": e.errors()}
        return jsonify(response), 400


@auth_bp.post("/refresh")
def refresh():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"success": False, "error": "missing token"}), 401

    token = auth_header.split(" ")[1]  # Bearer <token>

    return refresh_token(token)

@auth_bp.post("/logout")
def logout():
    auth_header = request.headers.get("Authorization")

    token = auth_header.split(" ")[1]  # Bearer <token>

    return logout_user(token)