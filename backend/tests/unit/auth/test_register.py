from unittest.mock import MagicMock

import pytest


@pytest.mark.parametrize(
    "existing_user, inserted_id, expected_status, expected_response",
    [
        (
            None,  # no existing user
            "12345",  # insert success
            201,
            {"success": True},
        ),
        (
            {"username": "test"},  # existing user
            None,
            400,
            {"success": False, "error": "Username already exists"},
        ),
    ],
)
def test_register_user(
    client, mocker, existing_user, inserted_id, expected_status, expected_response
):
    data = {"username": "testuser", "password": "password123"}

    mock_collection = mocker.patch("app.auth.register.user_collection")

    # mock find_one
    mock_collection.find_one.return_value = existing_user

    # mock insert_one
    mock_result = MagicMock()
    mock_result.inserted_id = inserted_id
    mock_collection.insert_one.return_value = mock_result

    response = client.post("/auth/register", json=data)

    assert response.status_code == expected_status  # noqa: F821
    assert response.json == expected_response


def test_register_duplicate_username(client, mocker):
    mock_collection = mocker.patch("app.auth.register.user_collection")
    mock_collection.find_one.return_value = {
        "username": "testusername",
        "password": "testpassword",
    }

    payload = {"username": "testusername", "password": "testpassword"}

    response = client.post("/auth/register", json=payload)

    body = response.get_json()

    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"] == "Username already exists"

def test_register_success(client, mocker):
    mock_collection = mocker.patch("app.auth.register.user_collection")
    mock_collection.find_one.return_value = None

    mock_collection.insert_one.inserted_id.return_value = "12345"

    payload = {"username": "testusername", "password": "testpassword"}

    response = client.post("/auth/register", json=payload)

    body = response.get_json()

    assert response.status_code == 201
    assert body["success"] is True

@pytest.mark.parametrize(
    "username, password",
    [
        ("", "password"),
        (None, "password"),
        ("username", ""),
        ("username", None),
    ]
)
def test_register_invalid_payload(client, mocker, username, password):
    payload = {
        "username": username,
        "password": password
    }

    response = client.post("/auth/register", json=payload)

    body = response.get_json()

    assert response.status_code == 400
    assert body["success"] is False
    assert "error" in body