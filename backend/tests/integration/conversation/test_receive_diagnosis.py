def test_receive_diagnosis(client, socket_client):
    # Create an account and login
    username = "test_username"
    password = "test_password"

    auth_payload = {"username": username, "password": password}

    client.post("/auth/register", json=auth_payload)

    signin_response = client.post("/auth/login", json=auth_payload)

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

    # Helper functions
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

    def resume_conversation(conversation_id, user_response):
        response = client.post(
            f"/resume/{conversation_id}",
            json={"user_response": user_response},
            headers=headers,
        )

        assert response.status_code == 200
        assert len(get_socket_messages(socket_client)) > 1

    # Sends the user query to resume the conversation
    resume_conversation(converation_id, "hi")

    assert socket_client.is_connected()

    # Answer to receive preliminary diagnosis
    resume_conversation(converation_id, "diagnosis")

    # Provide some initial symptom
    resume_conversation(converation_id, "I have headache")

    # Answer follow up question
    resume_conversation(converation_id, "Yes")

    # Required to answer 5 questions with either "Yes" or "No"
    for _ in range(5):
        resume_conversation(converation_id, "Yes")

    # Answer yes to ask follow question about diagnosed disease information
    resume_conversation(converation_id, "Yes")

    # Ask about a disease information
    resume_conversation(converation_id, "I would like to know more about migraine")

    # Answer no to terminate the current conversation
    resume_conversation(converation_id, "No")

    # Delete the current conversation
    delete_response = client.delete(
        f"/delete_conversation/{converation_id}", headers=headers
    )

    assert delete_response.status_code == 200
    assert delete_response.get_json()["success"] is True
