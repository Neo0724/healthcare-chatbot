from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.auth.refresh_token import refresh_token
from app.auth.login import login_user
from app.auth.register import register_user
from app.schemas.auth import LoginRequest
from app.schemas.auth import RegisterRequest

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
    data = request.get_json()

    if "refresh_token" not in data or not data["refresh_token"]:
        return jsonify({"success": False, "error": "Refresh token is required"}), 404

    return refresh_token(data["refresh_token"])
