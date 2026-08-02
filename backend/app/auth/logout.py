from flask import jsonify

from app.utils.mongodb_client import get_database

db = get_database()
refresh_token_collection = db["issued_refresh_token"]


def logout_user(refresh_token):
    refresh_token_collection.find_one_and_update(
        {"token": refresh_token}, {"$set": {"revoked": True}}
    )

    return jsonify({"success": True}), 200
