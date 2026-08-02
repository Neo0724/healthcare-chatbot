import asyncio

from dotenv import load_dotenv
from flask import Flask, current_app, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

from app.conversation.delete_conversation_history import delete_conversation_history
from app.conversation.retrieve_conversation_history import retrieve_conversation_history
from app.conversation.retrieve_conversation_message import retrieve_conversation_message
from app.conversation.store_conversation_history import store_conversation_history
from app.conversation.store_conversation_message import store_conversation_message
from app.conversation.update_conversation_message import update_conversation_message
from app.graph_flow import build_graph
from app.middlewares.jwt_middleware import jwt_required
from app.routes.auth import auth_bp
from app.routes.profile_management import profile_management_bp
from app.utils.neo4j_driver import get_neo4j_driver

load_dotenv()


def get_user_id(request):
    return str(request.user["sub"])


async def run_graph_and_response(
    graph_state, config, conversation_id, socket_io: SocketIO
):
    is_first_chunk = True

    msg = ""
    currentMsgId = ""

    async with AsyncSqliteSaver.from_conn_string("checkpoints.sqlite") as memory:
        graph = build_graph().compile(checkpointer=memory)

        async for chunk in graph.astream(
            graph_state,
            stream_mode=["updates", "messages"],
            version="v2",
            config=config,
        ):
            if chunk["type"] == "updates":
                for state in chunk["data"].values():
                    if state and "extracted_positive_symptoms" in state:
                        print(state["extracted_positive_symptoms"])

                    if state and "extracted_negative_symptoms" in state:
                        print(state["extracted_negative_symptoms"])

            elif (
                chunk["type"] == "messages"
                and "tags" in chunk["data"][1]
                and "user_message" in chunk["data"][1]["tags"]
            ):
                streamed_content = chunk["data"][0].content
                if is_first_chunk:
                    currentMsgId = store_conversation_message(
                        conversation_id=conversation_id,
                        content=streamed_content,
                        type="ai",
                    )
                    is_first_chunk = False

                msg += streamed_content
                # Handle emit to client
                socket_io.emit(
                    "message",
                    {"content": streamed_content, "id": currentMsgId, "is_last": False},
                    room=conversation_id,
                )

                if (
                    chunk["data"][0].chunk_position
                    and chunk["data"][0].chunk_position == "last"
                ):
                    socket_io.emit(
                        "message",
                        {
                            "content": streamed_content,
                            "id": currentMsgId,
                            "is_last": True,
                        },
                        room=conversation_id,
                    )
                    msg += streamed_content

                    # Synchronize with db when current message ended
                    update_conversation_message(
                        message_id=currentMsgId, new_content=msg.strip()
                    )
                    msg = ""
                    currentMsgId = ""
                    is_first_chunk = True

                # if "__interrupt__" in chunk["data"]:
                #     interrupt_value = chunk["data"]["__interrupt__"][0].value
                #     user_input = input(interrupt_value + "\nAnswer: ")
                #     state_input = Command(resume=user_input)
                #     config["configurable"]["thread_id"] = "patient_session_001"
                #     graph.update_state(state_input, config)

        # return retrieved_messages


def create_app():
    app = Flask(__name__)

    CORS(app, origins="*")

    socketio = SocketIO(app, cors_allowed_origins="*")

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(profile_management_bp)

    app.extensions["neo4j_driver"] = get_neo4j_driver()
    app.extensions["socketio"] = socketio

    @app.route("/")
    def home():
        return "Flask is working!"

    @app.route("/resume/<conversation_id>", methods=["POST"])
    def resume(conversation_id):
        data = request.get_json()
        neo4j_driver = current_app.extensions["neo4j_driver"]
        config = {
            "configurable": {"thread_id": conversation_id, "neo4j_driver": neo4j_driver}
        }
        user_response = data["user_response"]

        async def execute_flow():
            async with AsyncSqliteSaver.from_conn_string(
                "checkpoints.sqlite"
            ) as memory:
                graph = build_graph().compile(checkpointer=memory)

                current_state = await graph.aget_state(config)
                checkpoint = await memory.aget(config=config)

                store_conversation_message(
                    conversation_id=conversation_id, content=user_response, type="human"
                )

                if not current_state.next or not checkpoint:
                    await initialize(conversation_id=conversation_id)
                else:
                    await run_graph_and_response(
                        graph_state=Command(resume=user_response),
                        config=config,
                        conversation_id=conversation_id,
                        socket_io=socketio,
                    )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(execute_flow())
        finally:
            loop.close()

        return jsonify({"success": True}), 200

    async def initialize(conversation_id):
        neo4j_driver = current_app.extensions["neo4j_driver"]

        state_input = {
            "messages": [],
            "routing_choice": "",
            "extracted_positive_symptoms": [],
            "extracted_negative_symptoms": [],
            "asked_questions": [],
            "initial_disease_ids": [],
            "retrieved_disease_summary": [],
            "asked_questions_count": 0,
            "follow_up_agreement": "",
        }

        config = {
            "configurable": {"thread_id": conversation_id, "neo4j_driver": neo4j_driver}
        }

        await run_graph_and_response(
            graph_state=state_input,
            config=config,
            conversation_id=conversation_id,
            socket_io=socketio,
        )

    @app.route("/get_conversation_history")
    @jwt_required
    def get_conversation_history():
        user_id = get_user_id(request)
        return retrieve_conversation_history(user_id)

    @app.route("/get_conversation_message/<conversation_id>")
    @jwt_required
    def get_conversation_message(conversation_id: str):
        return retrieve_conversation_message(conversation_id)

    @app.route("/profile")
    @jwt_required
    def profile():
        return jsonify({"success": True, "user": request.user}), 200

    @app.route("/create_conversation", methods=["POST"])
    @jwt_required
    def create_conversation():
        data = request.get_json()
        user_input = str(data["user_input"])
        user_id = get_user_id(request)

        return store_conversation_history(user_id=user_id, user_query=user_input)

    @app.route("/delete_conversation/<conversation_id>", methods=["DELETE"])
    @jwt_required
    def delete_conversation(conversation_id):
        return delete_conversation_history(conversation_id)

    # WebSocket event
    @socketio.on("join_room")
    def join(data):
        room_id = data["conversation_id"]
        join_room(room_id)
        print(f"Joined room: {room_id}")

    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0", port=5000)
