import os

from dotenv import load_dotenv
from flask import request

from app.middlewares.jwt_middleware import jwt_required

load_dotenv()

SECRET = os.getenv("SECRET")


def create_test_route(app):
    @app.route("/test_jwt")
    @jwt_required
    def test_jwt():
        return {"success": True, "user": request.user}, 200
