
from flask import request
from app.middlewares.jwt_middleware import jwt_required
import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("SECRET")

def create_test_route(app):
    @app.route("/protected")
    @jwt_required
    def protected():
        return {
            "success": True,
            "user": request.user
        }, 200