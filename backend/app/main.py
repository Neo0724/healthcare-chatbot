from flask import Flask, current_app, jsonify, request
from neo4j import GraphDatabase
from dotenv import load_dotenv
from app.graph_flow import graph
from langgraph.types import Command
from app.middlewares.jwt_middleware import jwt_required
from app.routes.auth import auth_bp
import os

load_dotenv()

def run_graph_and_response(graph_state, config):
    retrieved_messages = []

    msg = ""

    for chunk in graph.stream(
        graph_state, stream_mode=["updates", "messages"], version="v2", config=config
    ):
        if chunk["type"] == "updates":
            print("Update Chunk")
            for _, state in chunk["data"].items():
                if state and "messages" in state:
                    for message in state["messages"]:
                        pass
                        # retrieved_messages.append(message.content)
                        # print(f"Updated message: {message.content}")
                
                if state and "extracted_positive_symptoms" in state:
                    print(state["extracted_positive_symptoms"])

                if state and "extracted_negative_symptoms" in state:
                    print(state["extracted_negative_symptoms"])
            
        elif chunk["type"] == "messages" and "tags" in chunk["data"][1] and "user_message" in chunk["data"][1]["tags"]:
            msg += chunk["data"][0].content
            if chunk["data"][0].chunk_position and chunk["data"][0].chunk_position == "last":
                retrieved_messages.append(msg)
                msg = ""


            # if "__interrupt__" in chunk["data"]:
            #     interrupt_value = chunk["data"]["__interrupt__"][0].value
            #     user_input = input(interrupt_value + "\nAnswer: ")
            #     state_input = Command(resume=user_input)
            #     config["configurable"]["thread_id"] = "patient_session_001"
            #     graph.update_state(state_input, config)

    return retrieved_messages

def create_app():
    app = Flask(__name__)

    app.register_blueprint(auth_bp, url_prefix="/auth")


    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
    )

    app.extensions["neo4j_driver"] = driver

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

        currentState = graph.get_state(config)

        user_response = data["user_response"]

        if not currentState.next:
            return initialize(conversation_id=conversation_id)

        return run_graph_and_response(Command(resume=user_response), config)


    @app.route("/get_messages/<conversation_id>")
    def get_messages(conversation_id):
        return f"ID is {conversation_id}"


    @app.route("/initialize/<conversation_id>", methods=["POST"])
    def initialize(conversation_id):
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

        return run_graph_and_response(state_input, config)

    @app.route("/profile")
    @jwt_required
    def profile():
        return jsonify(request.user), 200
    
    return app

if __name__ == "__main__":
    create_app().run(debug=True)
