import pytest


@pytest.mark.parametrize(
    "password_payload",
    [
        # 1. Missing or empty fields
        {"current_password": "", "new_password": ""},
        {"current_password": "validpassword", "new_password": ""},
        # 2. Current password too short (< 6 characters)
        {"current_password": "123", "new_password": "validpassword"},
        # 3. New password too short (< 6 characters)
        {"current_password": "validpassword", "new_password": "123"},
        # 4. New password too long (> 20 characters)
        {
            "current_password": "validpassword",
            "new_password": "thispasswordiswaytoolongtobeaccepted123",
        },
    ],
)
def test_change_password_invalid_password(client, mocker, password_payload):
    payload = password_payload
    response = client.post("/update-password", json=payload)

    assert response.status_code == 400
    assert response.json["success"] is False


def test_change_password_unmatch(client, mocker):
    mock_request = mocker.patch("app.routes.profile_management.get_user_id")
    mock_request.return_value = "507f1f77bcf86cd799439011"

    mock_user_collection = mocker.patch(
        "app.profile_management.change_password.user_collection"
    )

    mock_user_collection.find_one.return_value = {"password": "current_password"}

    mock_bcrypt = mocker.patch("app.profile_management.change_password.bcrypt")
    mock_bcrypt.checkpw.return_value = False

    payload = {"current_password": "unmatch_password", "new_password": "new_password"}

    response = client.post("/update-password", json=payload)

    body = response.get_json()

    assert response.status_code == 400
    assert body["success"] is False


def test_change_password_valid(client, mocker):
    mock_request = mocker.patch("app.routes.profile_management.get_user_id")
    mock_request.return_value = "507f1f77bcf86cd799439011"

    mock_user_collection = mocker.patch(
        "app.profile_management.change_password.user_collection"
    )

    mock_user_collection.find_one.return_value = {"password": "current_password"}

    mock_bcrypt = mocker.patch("app.profile_management.change_password.bcrypt")
    mock_bcrypt.checkpw.return_value = True

    payload = {"current_password": "current_password", "new_password": "new_password"}

    response = client.post("/update-password", json=payload)

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True
    mock_user_collection.find_one_and_update.assert_called_once()
