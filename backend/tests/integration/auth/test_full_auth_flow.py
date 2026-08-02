def test_full_auth_flow(client):
    username = "test_user"
    password = "test_password"

    new_username = "test_user_new"
    new_password = "test_password_new"

    payload = {"username": username, "password": password}

    signup_response = client.post("/auth/register", json=payload)

    signup_body = signup_response.get_json()

    assert signup_response.status_code == 201
    assert signup_body["success"] is True

    signin_response = client.post("/auth/login", json=payload)
    signin_body = signin_response.get_json()

    assert signin_response.status_code == 200
    assert signin_body["success"] is True
    assert "access_token" in signin_body
    assert "refresh_token" in signin_body

    access_token = signin_body["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    change_username_payload = {"username": new_username}

    change_username_response = client.post(
        "/update-username", json=change_username_payload, headers=headers
    )
    change_username_body = change_username_response.get_json()

    assert change_username_response.status_code == 200
    assert change_username_body["success"] is True

    change_password_payload = {
        "current_password": password,
        "new_password": new_password,
    }

    change_password_response = client.post(
        "/update-password", json=change_password_payload, headers=headers
    )
    change_password_body = change_password_response.get_json()

    assert change_password_response.status_code == 200
    assert change_password_body["success"] is True

    new_signin_payload = {"username": new_username, "password": new_password}

    new_signin_response = client.post("/auth/login", json=new_signin_payload)
    new_signin_body = new_signin_response.get_json()

    assert new_signin_response.status_code == 200
    assert new_signin_body["success"] is True
    assert "access_token" in new_signin_body
    assert "refresh_token" in new_signin_body
