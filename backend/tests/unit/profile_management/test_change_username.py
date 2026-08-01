import pytest


@pytest.mark.parametrize(
    "username",
    [None, "", "new_username_new_username1234567890"],
)
def test_change_username_invalid_username(client, mocker, username):
    payload = {"username": username}
    response = client.post("/update-username", json=payload)

    assert response.status_code == 400
    assert response.json["success"] is False


def test_change_username_duplicated(client, mocker):
    mock_request = mocker.patch("app.routes.profile_management.get_user_id")
    mock_request.return_value = "507f1f77bcf86cd799439011"

    mock_user_collection = mocker.patch(
        "app.profile_management.change_username.user_collection"
    )

    mock_user_collection.find_one.side_effect = [
        {"username": "exist"},
        {"username": "exist"},
    ]

    payload = {
        "username": "existed_username",
    }

    response = client.post("/update-username", json=payload)

    body = response.get_json()

    assert response.status_code == 400
    assert body["success"] is False


def test_change_username_valid(client, mocker):
    mock_request = mocker.patch("app.routes.profile_management.get_user_id")
    mock_request.return_value = "507f1f77bcf86cd799439011"

    mock_user_collection = mocker.patch(
        "app.profile_management.change_username.user_collection"
    )

    mock_user_collection.find_one.side_effect = [
        {"username": "exist"},
        None,
    ]

    payload = {
        "username": "new_username",
    }

    response = client.post("/update-username", json=payload)

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True
    mock_user_collection.find_one_and_update.assert_called_once()
