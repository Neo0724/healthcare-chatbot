import json
import os
from typing import Annotated, List, Literal
from langchain_huggingface import HuggingFaceEmbeddings
from neo4j import Driver, GraphDatabase
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from app.graph_queries.queries import (
    get_diseases_information,
    get_possible_diseases,
    narrow_down,
)
from app.llm.extract_disease_names import extract_disease_names
from app.llm.extract_patient_ans import extract_patient_ans
from app.llm.get_follow_up_questions import get_follow_up_questions
from app.llm.extract_symtoms import extract_medical_entities
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from dotenv import load_dotenv
from app.prompt_templates import ask_follow_up_question_prompt, explain_disease_prompt, preliminary_diagnosis_prompt
from app.prompt_templates import (
    refined_diagnosis_prompt,
)

load_dotenv()

os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "1"
os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"

URI = os.getenv("NEO4J_URL")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))


# =====================================================================
# 1. ENHANCED STATE DEFINITION
# =====================================================================
class ChatbotState(TypedDict):
    messages: Annotated[list, add_messages]
    user_messages: Annotated[List, add_messages]
    routing_choice: str  # "info" or "diagnosis"

    # Symptom & Question Tracking State
    extracted_positive_symptoms: List[str]
    extracted_negative_symptoms: List[str]
    asked_questions: List[str]  # Track exact text of previous questions
    initial_disease_ids: List[str]

    retrieved_disease_summary: List[str]
    asked_questions_count: int
    follow_up_agreement: str


# Initialize LLM
llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model="qwen3.5-4b",
    api_key="lm-studio",
    temperature=0,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)

# Initialize embedding model
embeddings_model = HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-base-v0.1")

# =====================================================================
# 2. UPDATED CONVERSATION NODES
# =====================================================================


def welcome_node(state: ChatbotState):
    # Pass an isolated, clean prompt to avoid triggering LM Studio's internal Jinja rendering issues
    system_instruction = (
        "You are a medical decision support assistant. Greet the patient politely and ask them "
        "if they would like to 'ask disease-related information' or 'get a preliminary diagnosis'."
    )

    response = llm.invoke(
        [SystemMessage(content=system_instruction)], config={"tags": ["user_message"]}
    )

    # IMPORTANT: DO NOT wrap again into AIMessage
    return {"messages": [response]}


def welcome_route_choice_node(state: ChatbotState):
    # Grab the last message text we generated to show the user
    last_msg = state["messages"][-1].content

    # The graph pauses here. Upon Command(resume=answer),
    # it picks up EXACTLY right here and assigns it to 'choice'.
    choice: str = interrupt(last_msg)

    print(f"Choice: {choice}")

    # Return the routing choice to the state so the conditional edge can read it
    return {"routing_choice": choice.strip().lower()}


# Disease lookup
def request_disease_info_node(state: ChatbotState):
    # First LLM call: Generates the prompt asking the user for a disease name
    response = llm.invoke(
        [
            SystemMessage(
                content="Ask the user which disease name they want to look up."
            )
        ],
        config={"tags": ["user_message"]},
    )

    # Store the prompt message in the state so it streams once
    return {"messages": [response]}


def collect_disease_to_lookup_node(state: ChatbotState):
    # Retrieve the question we just sent
    last_msg = state["messages"][-1].content

    # The graph pauses here. Upon Command(resume=answer),
    # execution wakes up exactly here and assigns the input to 'symptoms'.
    user_input: str = interrupt(last_msg)

    # Append the user's symptoms into the state history
    return {"user_messages": [user_input.strip()]}


def process_disease_info_node(state: ChatbotState, config: RunnableConfig):
    # Grab the text from the prompt we just sent out
    disease_names = state["user_messages"][-1]

    # 1. Extract name and embed
    extracted_disease_names: List[str] = extract_disease_names(disease_names)

    disease_embeddings = [
        embeddings_model.embed_query(d) for d in extracted_disease_names
    ]

    driver: Driver = config["configurable"].get("neo4j_driver")

    # 2. Query DB / Vector store
    records = get_diseases_information(
        driver, extracted_disease_names, disease_embeddings
    )

    retrieved_information = [
        {
            "disease_name": r.get("disease_name", ""),
            "score": r.get("score", 0),
            "definitions": r.get("definition_node", []),
            "symptom": r.get("symptom_node", []),
        }
        for r in records
    ]

    # Second LLM call: Generates the actual final educational breakdown
    response = llm.invoke(
        [
            SystemMessage(
                content=explain_disease_prompt.explain_disease_prompt_template.format(
                    user_message=disease_names,
                    user_disease=extracted_disease_names,
                    retrieved_information=retrieved_information,
                )
            )
        ],
        config={"tags": ["user_message"]},
    )

    # Append the user's query and the final AI answer into the chat history state
    return {"messages": [response]}


# Diagnosis
def request_initial_symptoms_node(state: ChatbotState):
    system_instruction = "You are a medical receptionist chatbot. Ask the patient to describe their symptoms in their own words."

    # Invoke the LLM to get the initial question
    response = llm.invoke(
        [SystemMessage(content=system_instruction)], config={"tags": ["user_message"]}
    )

    # Save the AI message immediately to state so it streams once and terminates
    return {"messages": [response]}


def collect_initial_symptoms_node(state: ChatbotState):
    # Retrieve the question we just sent
    last_msg = state["messages"][-1].content

    # The graph pauses here. Upon Command(resume=answer),
    # execution wakes up exactly here and assigns the input to 'symptoms'.
    symptoms: str = interrupt(last_msg)

    # Append the user's symptoms into the state history
    return {"user_messages": [symptoms.strip()]}


def process_and_diagnose_node(state: ChatbotState, config: RunnableConfig):
    """Processes initial response, extracts primary symptoms, and records them."""
    # 1. Grab the last message the user sent describing their symptoms
    user_initial_text = state["user_messages"][-1].content

    print("Initial symptoms: ", user_initial_text)

    # 2. RUN YOUR EXTRACTION FUNCTION HERE
    # Example: extracted = your_extraction_tool(user_initial_text)
    extracted_entities = extract_medical_entities(user_initial_text)

    # print(f"Extracted Entities: {extracted_entities}")

    positive_symptoms = list(extracted_entities.positive_symptoms)
    negative_symptoms = list(extracted_entities.negative_symptoms)

    positive_embedding = embeddings_model.embed_query(",".join(positive_symptoms))
    negative_embedding = embeddings_model.embed_query(",".join(negative_symptoms))

    driver: Driver = config["configurable"].get("neo4j_driver")

    db_results = get_possible_diseases(driver, positive_embedding, negative_embedding)

    retrieved_disease_summary = [
        {
            "disease_name": r.get("disease_name", ""),
            "match_score": r.get("post_score", 0),
            "disease_symptom_details": r.get("symptom_node", []),
        }
        for r in db_results
    ]

    print(f"Retrieved possible diseases: {retrieved_disease_summary}")

    initial_disease_ids = [r.get("disease_id", "") for r in db_results]

    # Format the prompt with the complete JSON structure so it has access to scores and summaries
    formatted_prompt = (
        preliminary_diagnosis_prompt.preliminary_diagnosis_prompt_template.format(
            medical_data=json.dumps(retrieved_disease_summary, indent=2),
            user_symptoms=json.dumps(user_initial_text, indent=2),
        )
    )

    # USE THIS TAG TO FILTER
    response = llm.invoke(
        [SystemMessage(content=formatted_prompt)], config={"tags": ["user_message"]}
    )

    # Update state: initialize lists and add initial symptoms to positive tracker
    return {
        "messages": [response],
        "extracted_positive_symptoms": positive_symptoms,
        "extracted_negative_symptoms": negative_symptoms,
        "retrieved_disease_summary": retrieved_disease_summary,
        "asked_questions_count": 0,
        "initial_disease_ids": initial_disease_ids,
    }


def request_agreement_on_follow_up_node(state: ChatbotState):
    # First LLM call: Generates the prompt asking the user for a disease name
    response = llm.invoke(
        [
            SystemMessage(
                content="Ask the user whether he or she wants to answer follow up questions to refine preliminary diagnosis"
            )
        ],
        config={"tags": ["user_message"]},
    )

    # Store the prompt message in the state so it streams once
    return {"messages": [response]}


def collect_agreement_on_follow_up_node(state: ChatbotState):
    # Retrieve the question we just sent
    last_msg = state["messages"][-1].content

    # The graph pauses here. Upon Command(resume=answer),
    # execution wakes up exactly here and assigns the input to 'symptoms'.
    agreement: str = interrupt(last_msg)

    # Append the user's symptoms into the state history
    return {
        "user_messages": [agreement.strip()],
        "follow_up_agreement": agreement.strip(),
    }


def ask_follow_up_question_node(state: ChatbotState):
    """Uses tracked symptoms and previous questions to generate the next question."""
    current_count = state.get("asked_questions_count", 0) + 1

    print(f"Current count: {current_count}")

    current_positives = state.get("extracted_positive_symptoms", [])
    current_negatives = state.get("extracted_negative_symptoms", [])
    past_questions = state.get("asked_questions", [])
    retrieved_disease_summary = state.get("retrieved_disease_summary", "")

    response = get_follow_up_questions(
        retrieved_disease_summary, current_positives, current_negatives, past_questions
    )

    follow_up_question = str(response.question)
    reason = str(response.reason)

    # Compile the prompt template with your variables
    formatted_prompt = (
        ask_follow_up_question_prompt.ask_follow_up_question_prompt_template.format(
            reason=reason, question=follow_up_question
        )
    )

    # Formulate output for the conversation stream using SystemMessage
    response = llm.invoke(
        [SystemMessage(content=formatted_prompt)], config={"tags": ["user_message"]}
    )

    return {
        "messages": [response],
        "asked_questions_count": current_count,
        "asked_questions": past_questions + [follow_up_question],
    }


def collect_follow_up_response_node(state: ChatbotState):
    # Retrieve the question we just sent
    last_msg = state["messages"][-1].content

    # The graph pauses here. Upon Command(resume=answer),
    # execution wakes up exactly here and assigns the input to 'symptoms'.
    follow_up_answer: str = interrupt(last_msg)

    # Append the user's symptoms into the state history
    return {
        "user_messages": [follow_up_answer.strip()],
    }


def process_follow_up_response_node(state: ChatbotState):
    asked_question = state["messages"][-1].content
    user_answer = state["user_messages"][-1].content

    current_positives = state.get("extracted_positive_symptoms", [])
    current_negatives = state.get("extracted_negative_symptoms", [])

    extracted_entities = extract_patient_ans(
        answer=user_answer, question=asked_question
    )

    positive_symptoms = list(extracted_entities.positive_symptoms)
    negative_symptoms = list(extracted_entities.negative_symptoms)

    return {
        "extracted_positive_symptoms": positive_symptoms + current_positives,
        "extracted_negative_symptoms": negative_symptoms + current_negatives,
    }


def final_refined_diagnosis_node(state: ChatbotState, config: RunnableConfig):
    """Uses full historic lists of positive/negative symptoms for the ultimate query."""

    current_positives = state.get("extracted_positive_symptoms", "")
    current_negatives = state.get("extracted_negative_symptoms", "")
    initial_disease_ids = state.get("initial_disease_ids")

    positive_embedding = embeddings_model.embed_query(",".join(current_positives))
    negative_embedding = embeddings_model.embed_query(",".join(current_negatives))

    driver: Driver = config["configurable"].get("neo4j_driver")

    records = narrow_down(
        driver, positive_embedding, negative_embedding, initial_disease_ids
    )

    for index, record in enumerate(records):
        print(
            f"Rank: {index + 1} | FSN: {record.get('disease_name', '')} | Score: {record.get('post_score', ''):.4f}"
        )

    refined_results = [
        {
            "disease_name": r.get("disease_name", ""),
            "match_score": float(r.get("post_score", 0)),
            "symptom_details": r.get("symptom_node", []),
        }
        for r in records
    ]

    refined_results.sort(key=lambda x: x["match_score"], reverse=True)

    print(f"Refined Results:\n{refined_results}\n\n")

    response = llm.invoke(
        [
            SystemMessage(
                content=refined_diagnosis_prompt.refined_diagnosis_prompt_template
            )
        ],
        config={"tags": ["user_message"]},
    )
    return {"messages": [response]}


# =====================================================================
# 3. ROUTING LOGIC
# =====================================================================
def route_after_welcome(
    state: ChatbotState,
) -> Literal["request_disease_info", "request_symptoms"]:
    if state.get("routing_choice", "").strip().lower() in ["info", "disease"]:
        return "request_disease_info"
    return "request_symptoms"


def route_after_preliminary(
    state: ChatbotState,
) -> Literal["ask_follow_up", "final_refined_diagnosis"]:
    if "yes" in state.get("follow_up_agreement", "").strip().lower():
        return "ask_follow_up"
    return "final_refined_diagnosis"


def route_follow_up_loop(
    state: ChatbotState,
) -> Literal["ask_follow_up", "final_refined_diagnosis"]:
    if state.get("asked_questions_count", 0) >= 5:
        return "final_refined_diagnosis"
    return "ask_follow_up"


# =====================================================================
# 4. INITIALIZING & COMPILING THE GRAPH (THE FIX)
# =====================================================================
# Step A: Instantiate the StateGraph with your ChatbotState definition

memory = MemorySaver()

graph = (
    StateGraph(ChatbotState)
    .add_node("welcome", welcome_node)
    .add_node("welcome_route_choice", welcome_route_choice_node)
    # Disease info
    .add_node("request_disease_info", request_disease_info_node)
    .add_node("collect_disease_to_lookup", collect_disease_to_lookup_node)
    .add_node("process_disease_info", process_disease_info_node)
    # Diagnosis
    .add_node("request_symptoms", request_initial_symptoms_node)
    .add_node("collect_initial_symptoms", collect_initial_symptoms_node)
    .add_node("process_and_diagnose", process_and_diagnose_node)
    .add_node(
        "request_agreement_on_follow_up_node", request_agreement_on_follow_up_node
    )
    .add_node(
        "collect_agreement_on_follow_up_node", collect_agreement_on_follow_up_node
    )
    .add_node("ask_follow_up", ask_follow_up_question_node)
    .add_node("collect_follow_up_response", collect_follow_up_response_node)
    .add_node("process_follow_up_response", process_follow_up_response_node)
    .add_node("final_refined_diagnosis", final_refined_diagnosis_node)
    # Step C: Set up edges and conditional routers
    .add_edge(START, "welcome")
    .add_edge("welcome", "welcome_route_choice")
    .add_conditional_edges(
        "welcome_route_choice",
        route_after_welcome,
        {
            "request_disease_info": "request_disease_info",
            "request_symptoms": "request_symptoms",
        },
    )
    .add_edge("request_disease_info", "collect_disease_to_lookup")
    .add_edge("collect_disease_to_lookup", "process_disease_info")
    .add_edge("process_disease_info", END)
    .add_edge("request_symptoms", "collect_initial_symptoms")
    .add_edge("collect_initial_symptoms", "process_and_diagnose")
    .add_edge("process_and_diagnose", "request_agreement_on_follow_up_node")
    .add_edge(
        "request_agreement_on_follow_up_node", "collect_agreement_on_follow_up_node"
    )
    .add_conditional_edges(
        "collect_agreement_on_follow_up_node",
        route_after_preliminary,
        {
            "ask_follow_up": "ask_follow_up",
            "final_refined_diagnosis": "final_refined_diagnosis",
        },
    )
    .add_edge("ask_follow_up", "collect_follow_up_response")
    .add_edge("collect_follow_up_response", "process_follow_up_response")
    .add_conditional_edges(
        "process_follow_up_response",
        route_follow_up_loop,
        {
            "ask_follow_up": "ask_follow_up",
            "final_refined_diagnosis": "final_refined_diagnosis",
        },
    )
    .add_edge("final_refined_diagnosis", END)
    .compile(checkpointer=memory)
)


def run_graph(graph, driver: Driver):
    # Define your initial state setup

    print("--- Kicking off Graph ---")
    state_input = {
        "messages": [],
        "routing_choice": "diagnosis",  # Your router reads this
        "extracted_positive_symptoms": [],
        "extracted_negative_symptoms": [],
        "asked_questions": [],  # Track exact text of previous questions
        "initial_disease_ids": [],
        "retrieved_disease_summary": [],
        "asked_questions_count": 0,
        "follow_up_agreement": "",
    }

    # Pass configuration (like the Neo4j driver)
    config = {
        "configurable": {"thread_id": "patient_session_001", "neo4j_driver": driver}
    }

    while True:
        for chunk in graph.stream(
            state_input,
            stream_mode=["updates", "messages"],
            version="v2",
            config=config,
        ):
            if chunk["type"] == "updates":
                for _, state in chunk["data"].items():
                    if state and "messages" in state:
                        for message in state["messages"]:
                            print(f"Updated message: {message.content}")

                    if state and "extracted_positive_symptoms" in state:
                        print(state["extracted_positive_symptoms"])

                    if state and "extracted_negative_symptoms" in state:
                        print(state["extracted_negative_symptoms"])

                if "__interrupt__" in chunk["data"]:
                    interrupt_value = chunk["data"]["__interrupt__"][0].value
                    user_input = input(interrupt_value + "\nAnswer: ")
                    state_input = Command(resume=user_input)
                    config["configurable"]["thread_id"] = "patient_session_001"

            elif (
                chunk["type"] == "messages"
                and "tags" in chunk["data"][1]
                and "user_message" in chunk["data"][1]["tags"]
            ):
                pass
                # print(f"CHUNK MESSAGES:\n{chunk['data']}")
                # if (
                #     chunk["data"][0].chunk_position
                #     and chunk["data"][0].chunk_position == "last"
                # ):
                #     print("CHUNK MESSAGES ENDED")


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    # Define your initial state setup
    run_graph(graph, driver)
