from bson import ObjectId
import pytest


def test_login_incorrect_password(client, mocker):
    mock_collection = mocker.patch("app.auth.login.user_collection")
    mock_collection.find_one.return_value = {
        "_id": ObjectId(),
        "username": "testuser",
        "password": "testpassword",
    }

    mock_bcrypt = mocker.patch("app.auth.login.bcrypt")
    mock_bcrypt.checkpw.return_value = False

    payload = {"username": "testuser", "password": "testpassworderror"}

    response = client.post("/auth/login", json=payload)

    body = response.get_json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error"] == "Password incorrect"


def test_login_incorrect_username(client, mocker):
    mock_collection = mocker.patch("app.auth.login.user_collection")
    mock_collection.find_one.return_value = None

    payload = {"username": "testuser", "password": "testpassworderror"}

    response = client.post("/auth/login", json=payload)

    body = response.get_json()

    assert response.status_code == 404
    assert body["success"] is False
    assert body["error"] == "Username not found"


def test_login_success(client, mocker):
    mock_collection = mocker.patch("app.auth.login.user_collection")
    mock_collection.find_one.return_value = {
        "_id": ObjectId(),
        "username": "testuser",
        "password": "testpassword",
    }

    mock_bcrypt = mocker.patch("app.auth.login.bcrypt")
    mock_bcrypt.checkpw.return_value = True

    payload = {"username": "testuser", "password": "testpassword"}

    response = client.post("/auth/login", json=payload)

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True
    assert "error" not in body
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.parametrize(
    "username, password",
    [
        ("", "password"),
        (None, "password"),
        ("username", ""),
        ("username", None),
    ],
)
def test_login_invalid_payload(client, mocker, username, password):
    payload = {"username": username, "password": password}

    response = client.post("/auth/login", json=payload)

    body = response.get_json()

    assert response.status_code == 400
    assert body["success"] is False
    assert "error" in body
