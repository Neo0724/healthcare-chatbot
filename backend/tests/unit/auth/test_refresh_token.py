import jwt


def test_refresh_token_missing_token(client, mocker):
    headers = {}

    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == 401
    assert response.json["success"] is False


def test_refresh_token_expired(client, mocker):
    headers = {"Authorization": "Bearer token"}

    mock_decode = mocker.patch("app.auth.refresh_token.jwt.decode")

    mock_decode.side_effect = jwt.ExpiredSignatureError("Signature has expired")

    response = client.post("/auth/refresh", headers=headers)

    body = response.get_json()

    assert response.status_code == 401
    assert body["success"] is False


def test_refresh_token_invalid(client, mocker):
    headers = {"Authorization": "Bearer token"}

    mock_decode = mocker.patch("app.auth.refresh_token.jwt.decode")

    mock_decode.side_effect = jwt.InvalidTokenError("Signature has expired")

    response = client.post("/auth/refresh", headers=headers)

    body = response.get_json()

    assert response.status_code == 401
    assert body["success"] is False


def test_refresh_token_db_missing(client, mocker):
    headers = {"Authorization": "Bearer token"}

    mock_decode = mocker.patch("app.auth.refresh_token.jwt.decode")
    mock_decode.return_value = {"sub": "507f1f77bcf86cd799439011", "username": "test"}

    mock_refresh_token_collection = mocker.patch(
        "app.auth.refresh_token.refresh_token_collection"
    )
    mock_refresh_token_collection.find_one.return_value = None

    response = client.post("/auth/refresh", headers=headers)

    body = response.get_json()

    assert response.status_code == 401
    assert body["success"] is False


def test_refresh_token_revoked(client, mocker):
    headers = {"Authorization": "Bearer token"}

    mock_decode = mocker.patch("app.auth.refresh_token.jwt.decode")
    mock_decode.return_value = {"sub": "507f1f77bcf86cd799439011", "username": "test"}

    mock_refresh_token_collection = mocker.patch(
        "app.auth.refresh_token.refresh_token_collection"
    )
    mock_refresh_token_collection.find_one.return_value = {
        "token": "1234",
        "revoked": True,
    }

    response = client.post("/auth/refresh", headers=headers)

    body = response.get_json()

    assert response.status_code == 401
    assert body["success"] is False


def test_refresh_token_valid(client, mocker):
    headers = {"Authorization": "Bearer token"}

    mock_decode = mocker.patch("app.auth.refresh_token.jwt.decode")
    mock_decode.return_value = {"sub": "507f1f77bcf86cd799439011", "username": "test"}

    mock_refresh_token_collection = mocker.patch(
        "app.auth.refresh_token.refresh_token_collection"
    )
    mock_refresh_token_collection.find_one.return_value = {
        "token": "1234",
        "revoked": False,
    }

    mock_encode = mocker.patch("app.auth.refresh_token.jwt.encode")
    mock_encode.return_value = "test_encoded_jwt_token"

    response = client.post("/auth/refresh", headers=headers)

    body = response.get_json()

    assert response.status_code == 200
    assert body["success"] is True
    mock_refresh_token_collection.find_one_and_update.assert_called_once()
    mock_refresh_token_collection.insert_one.assert_called_once()
    assert body["access_token"] == mock_encode.return_value
    assert body["refresh_token"] == mock_encode.return_value
