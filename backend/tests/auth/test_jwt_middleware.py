import jwt
from datetime import datetime, timezone, timedelta
from app.routes.test_route import SECRET

def generate_token(expiration=None):
    payload = {
        "sub": "123",
        "username": "testuser",
        "exp": expiration or (
            datetime.now(timezone.utc) + timedelta(minutes=30)
        )
    }

    return jwt.encode(
        payload,
        SECRET,
        algorithm="HS256"
    )


def test_missing_token(client):
    response = client.get("/protected")

    assert response.status_code == 401
    assert response.json == {
        "error": "missing token"
    }


def test_invalid_token(client):
    response = client.get(
        "/protected",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401
    assert response.json == {
        "error": "invalid token"
    }


def test_expired_token(client):
    token = generate_token(
        datetime.now(timezone.utc) - timedelta(minutes=1)
    )

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
    assert response.json == {
        "error": "token expired"
    }


def test_valid_token(client):
    token = generate_token()

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["user"]["username"] == "testuser"