from flask import Blueprint, jsonify, request

from app.middlewares.jwt_middleware import jwt_required
from app.profile_management.change_password import change_password
from app.profile_management.change_username import change_username

profile_management_bp = Blueprint("profile_management", __name__)


def get_user_id(request):
    return request.user["sub"]


@profile_management_bp.post("/update-username")
@jwt_required
def update_username():
    data = request.get_json()

    if not data["username"]:
        return jsonify({"success": False, "error": "Username is required"}), 400

    username = str(data["username"]).strip()

    if len(username) == 0:
        return jsonify(
            {"success": False, "error": "At least 1 character is required"}
        ), 400
    elif len(username) > 20:
        return jsonify(
            {"success": False, "error": "Only up-to 20 characters are allowed"}
        ), 400

    user_id = get_user_id(request)

    return change_username(username, user_id)


@profile_management_bp.post("/update-password")
@jwt_required
def update_password():
    data = request.get_json()

    if not data["current_password"] or not data["new_password"]:
        return jsonify(
            {"success": False, "error": "Current password and new password is required"}
        ), 400

    current_password = str(data["current_password"]).strip()
    new_password = str(data["new_password"]).strip()

    if len(current_password) < 6:
        return jsonify(
            {
                "success": False,
                "error": {"current_password": "At least six characters are required"},
            }
        ), 400

    if len(new_password) < 6:
        return jsonify(
            {
                "success": False,
                "error": {"new_password": "At least six characters are required"},
            }
        ), 400

    elif len(new_password) > 20:
        return jsonify(
            {
                "success": False,
                "error": {"new_password": "Only up-to 20 characters are allowed"},
            }
        ), 400

    user_id = get_user_id(request)
    return change_password(current_password, new_password, user_id)
