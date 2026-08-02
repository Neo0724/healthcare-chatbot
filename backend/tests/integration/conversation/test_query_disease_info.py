def test_query_disease_info(client, socket_client):
    # Create an account and login
    username = "test_username"
    password = "test_password"

    auth_payload = {"username": username, "password": password}

    client.post("/auth/register", json=auth_payload)

    signin_response = client.post("/auth/login", json=auth_payload)

    assert signin_response.status_code == 200
    assert "access_token" in signin_response.get_json()

    access_token = signin_response.get_json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a new conversation
    initialize_chat_response = client.post(
        "/create_conversation", json={"user_input": "hi"}, headers=headers
    )

    initialize_chat_body = initialize_chat_response.get_json()

    assert initialize_chat_response.status_code == 200
    assert "conversation_id" in initialize_chat_body

    converation_id = initialize_chat_body["conversation_id"]

    # Join the room of conversation id
    socket_client.emit("join_room", {"conversation_id": converation_id})

    # Sends the user query to resume the conversation
    client.post(
        f"/resume/{converation_id}", json={"user_response": "hi"}, headers=headers
    )

    assert socket_client.is_connected()

    def get_socket_messages(socket_client):
        all_chunks = []
        is_complete = False

        while not is_complete:
            received_events = socket_client.get_received()
            for event in received_events:
                # Replace "message_chunk" with whatever event name your server emits for stream parts
                if event["name"] == "message":
                    print(f"Received event: {event}")
                    payload = event["args"]
                    all_chunks.append(payload.get("content", ""))
                    # Check your stop condition
                    if payload.get("is_last") is True:
                        return all_chunks

    assert len(get_socket_messages(socket_client)) > 1

    # Answer to search for disease information
    client.post(
        f"/resume/{converation_id}",
        json={"user_response": "info"},
        headers=headers,
    )

    assert len(get_socket_messages(socket_client)) > 1

    # Provide the disease name
    client.post(
        f"/resume/{converation_id}",
        json={"user_response": "I would like to know more about diabetes"},
        headers=headers,
    )

    assert len(get_socket_messages(socket_client)) > 1

    # Answer yes to ask about other disease
    client.post(
        f"/resume/{converation_id}",
        json={"user_response": "yes"},
        headers=headers,
    )

    assert len(get_socket_messages(socket_client)) > 1

    # Ask another disease info
    client.post(
        f"/resume/{converation_id}",
        json={"user_response": "I would like to know about dengue"},
        headers=headers,
    )


    assert len(get_socket_messages(socket_client)) > 1

    # Answer no to terminate current conversation
    client.post(
        f"/resume/{converation_id}",
        json={"user_response": "no"},
        headers=headers,
    )

    assert len(get_socket_messages(socket_client)) > 1

    # Delete the current conversation
    delete_response = client.delete(f"/delete_conversation/{converation_id}", headers=headers)

    assert delete_response.status_code == 200
    assert delete_response.get_json()["success"] is True