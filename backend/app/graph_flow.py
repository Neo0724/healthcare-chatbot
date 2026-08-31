import json
import os
from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.types import Command, interrupt
from neo4j import Driver
from typing_extensions import TypedDict

from app.graph_queries.queries import (
    get_diseases_information,
    get_possible_diseases,
    narrow_down,
)
from app.llm.extract_disease_names import extract_disease_names
from app.llm.extract_follow_up_question_symptom import (
    extract_follow_up_question_symptom,
)
from app.llm.extract_symtoms import extract_symptoms
from app.llm.get_follow_up_questions import get_follow_up_questions
from app.prompt_templates import (
    ask_follow_up_question_prompt,
    explain_disease_prompt,
    preliminary_diagnosis_prompt,
    refined_diagnosis_prompt,
)
from app.utils.get_embedding_model import get_embedding_model
from app.utils.get_reranker_model import get_reranker_model

load_dotenv()

os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "1"
os.environ["HF_HOME"] = "C:/hf_cache"
os.environ["HF_TOKEN"] = "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"


# =====================================================================
# 1. ENHANCED STATE DEFINITION
# =====================================================================
class ChatbotState(TypedDict):
    messages: Annotated[list, add_messages]
    user_messages: Annotated[list, add_messages]
    routing_choice: str  # "info" or "diagnosis"

    # Symptom & Question Tracking State
    extracted_positive_symptoms: list[str]
    extracted_negative_symptoms: list[str]
    asked_questions: list[str]  # Track exact text of previous questions
    initial_disease_ids: list[str]

    retrieved_disease_summary: list[str]
    asked_questions_count: int
    follow_up_agreement: str
    diagnosis_result_query_choice: str
    ask_more_disease_info_choice: str


# Initialize LLM
llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model=os.getenv("LLM_MODEL"),
    api_key="lm-studio",
    temperature=0,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)


def rerank_contexts(user_query, contexts):
    pairs = [[user_query, context] for context in contexts]

    scores = get_reranker_model().predict(pairs)

    updated_context = sorted(zip(scores, pairs), key=lambda x: x[0], reverse=True)

    cleaned = [context[1][1] for context in updated_context]

    return cleaned[:15]


# =====================================================================
# 2. UPDATED CONVERSATION NODES
# =====================================================================


def welcome_node(state: ChatbotState):
    # Pass an isolated, clean prompt to avoid triggering LM Studio's internal Jinja rendering issues
    system_instruction = (
        "You are a medical decision support assistant. Greet the patient politely and ask them "
        "if they would like to 'ask disease-related information such as what is the disease, treatment and symptoms' or 'get a preliminary diagnosis'."
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
    user_query = state["user_messages"][-1]

    print(f"\nUser Query:\n{user_query}")

    # 1. Extract name and embed
    extracted_disease_names: list[str] = extract_disease_names(user_query)

    embedding_model = get_embedding_model()

    disease_embeddings = [
        embedding_model.embed_query(d) for d in extracted_disease_names
    ]

    driver: Driver = config["configurable"].get("neo4j_driver")

    # 2. Query DB / Vector store
    records = get_diseases_information(
        driver, extracted_disease_names, disease_embeddings
    )

    contexts = []

    for record in records:
        for definition in record.get("definition_node"):
            contexts.append(
                f"### Disease Name: {record.get('disease_name')}\n### Score: {round(float(record.get('score')), 2)}\n### Retrieved Disease Definitions: {str(definition)}"
            )

        for symptom in record.get("symptom_node"):
            contexts.append(
                f"### Disease Name: {record.get('disease_name')}\n### Score: {round(float(record.get('score')), 2)}\n### Retrieved Disease Symptoms: {str(symptom)}"
            )

        for treatment in record.get("treatment_node"):
            contexts.append(
                f"### Disease Name: {record.get('disease_name')}\n### Score: {round(float(record.get('score')), 2)}\n### Retrieved Disease Treatment: {str(treatment)}"
            )

    reranked_context = rerank_contexts(user_query=user_query.content, contexts=contexts)

    # Second LLM call: Generates the actual final educational breakdown
    response = llm.invoke(
        [
            SystemMessage(
                content=explain_disease_prompt.explain_disease_prompt_template.format(
                    user_message=user_query,
                    user_disease=extracted_disease_names,
                    retrieved_information=reranked_context,
                )
            )
        ],
        config={"tags": ["user_message"]},
    )

    # Append the user's query and the final AI answer into the chat history state
    return {"messages": [response]}


def request_ask_more_disease_info(state: ChatbotState):
    system_instruction = (
        "Ask the user whether if he or she would like to ask for more information about a disease. "
        "User should be able to answer in 'Yes' or 'No'"
    )

    # Invoke the LLM to get the initial question
    response = llm.invoke(
        [SystemMessage(content=system_instruction)], config={"tags": ["user_message"]}
    )

    # Save the AI message immediately to state so it streams once and terminates
    return {"messages": [response]}


def collect_ask_more_disease_info(state: ChatbotState):
    # Retrieve the question we just sent
    last_msg = state["messages"][-1].content

    # The graph pauses here. Upon Command(resume=answer),
    # execution wakes up exactly here and assigns the input to 'symptoms'.
    user_input: str = interrupt(last_msg)

    # Append the user's symptoms into the state history
    return {
        "user_messages": [user_input.strip()],
        "ask_more_disease_info_choice": user_input.strip(),
    }


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
    extracted_entities = extract_symptoms(user_initial_text)

    # print(f"Extracted Entities: {extracted_entities}")

    positive_symptoms = list(extracted_entities.positive_symptoms)
    # negative_symptoms = list(extracted_entities.negative_symptoms)
    negative_symptoms = []

    embedding_model = get_embedding_model()

    positive_embedding = embedding_model.embed_query(",".join(positive_symptoms))
    # negative_embedding = get_embedding_model().embed_query(",".join(negative_symptoms))
    negative_embedding = embedding_model.embed_query(",".join(negative_symptoms))

    driver: Driver = config["configurable"].get("neo4j_driver")

    db_results = get_possible_diseases(driver, positive_embedding, negative_embedding)

    retrieved_disease_summary = [
        {
            "disease_name": r.get("disease_name", ""),
            "match_score": round(float(r.get("post_score", 0)), 2),
            "disease_symptom_details": r.get("symptom_node", []),
        }
        for r in db_results
    ]

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
                content="Ask the user whether he or she wants to answer follow up questions to refine preliminary diagnosis. If no, a final refined preliminary diagnosis will be provided"
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

    extracted_entities = extract_follow_up_question_symptom(
        input=user_answer, question=asked_question
    )

    positive_symptoms = list(extracted_entities.positive_symptoms)
    negative_symptoms = list(extracted_entities.negative_symptoms)

    return {
        "extracted_positive_symptoms": list(set(positive_symptoms + current_positives)),
        "extracted_negative_symptoms": list(set(negative_symptoms + current_negatives)),
    }


def final_refined_diagnosis_node(state: ChatbotState, config: RunnableConfig):
    """Uses full historic lists of positive/negative symptoms for the ultimate query."""

    current_positives = state.get("extracted_positive_symptoms", "")
    # current_negatives = state.get("extracted_negative_symptoms", "")
    current_negatives = []
    initial_disease_ids = state.get("initial_disease_ids")

    embedding_model = get_embedding_model()

    positive_embedding = embedding_model.embed_query(",".join(current_positives))
    # negative_embedding = get_embedding_model().embed_query(",".join(current_negatives))
    negative_embedding = embedding_model.embed_query(",".join(current_negatives))

    driver: Driver = config["configurable"].get("neo4j_driver")

    records = narrow_down(
        driver, positive_embedding, negative_embedding, initial_disease_ids
    )

    # for index, record in enumerate(records):
    #     print(
    #         f"Rank: {index + 1} | FSN: {record.get('disease_name', '')} | Score: {record.get('post_score', ''):.4f}"
    #     )

    refined_results = [
        {
            "disease_name": r.get("disease_name", ""),
            "match_score": round(float(r.get("post_score", 0)), 2),
            "symptom_details": r.get("symptom_node", []),
        }
        for r in records
    ]

    refined_results.sort(key=lambda x: x["match_score"], reverse=True)

    # print(f"Refined Results:\n{refined_results}\n\n")

    response = llm.invoke(
        [
            SystemMessage(
                content=refined_diagnosis_prompt.refined_diagnosis_prompt_template.format(
                    current_positives=current_positives,
                    current_negatives=current_negatives,
                    refined_results=refined_results,
                )
            )
        ],
        config={"tags": ["user_message"]},
    )
    return {"messages": [response]}


def request_diagnosis_result_query_node(state: ChatbotState):
    response = llm.invoke(
        [
            SystemMessage(
                content="Ask the user whether he or she would like to know more about the diagnosed diseases information."
                "User should be able to answer in 'Yes' or 'No'"
            )
        ],
        config={"tags": ["user_message"]},
    )

    # Store the prompt message in the state so it streams once
    return {"messages": [response]}


def collect_diagnosis_result_query_node(state: ChatbotState):
    # Retrieve the question we just sent
    last_msg = state["messages"][-1].content

    # The graph pauses here. Upon Command(resume=answer),
    # execution wakes up exactly here and assigns the input to 'symptoms'.
    user_input: str = interrupt(last_msg)

    # Append the user's symptoms into the state history
    return {
        "user_messages": [user_input.strip()],
        "diagnosis_result_query_choice": user_input.strip(),
    }


def end_node(state: ChatbotState):
    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "Conclude the conversation warmly and professionally. "
                    "Inform the user that if they wish to start a new conversation at any time, "
                    "they can simply send a 'hi' message, and you will be ready to provide medical assistance."
                )
            )
        ],
        config={"tags": ["user_message"]},
    )

    # Store the prompt message in the state so it streams once
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


def route_after_asking_disease_info(
    state: ChatbotState,
) -> Literal["request_disease_info", "end_node"]:
    if "yes" in state.get("ask_more_disease_info_choice", "").strip().lower():
        return "request_disease_info"
    return "end_node"


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


def route_diagnosis_result_query_node(
    state: ChatbotState,
) -> Literal["request_disease_info", "end_node"]:
    if "yes" in state.get("diagnosis_result_query_choice", "").strip().lower():
        return "request_disease_info"
    return "end_node"


# =====================================================================
# 4. INITIALIZING & COMPILING THE GRAPH (THE FIX)
# =====================================================================
# Step A: Instantiate the StateGraph with your ChatbotState definition


def build_graph():
    graph = (
        StateGraph(ChatbotState)
        .add_node("welcome", welcome_node)
        .add_node("welcome_route_choice", welcome_route_choice_node)
        # Disease info
        .add_node("request_disease_info", request_disease_info_node)
        .add_node("collect_disease_to_lookup", collect_disease_to_lookup_node)
        .add_node("process_disease_info", process_disease_info_node)
        .add_node("request_ask_more_disease_info", request_ask_more_disease_info)
        .add_node("collect_ask_more_disease_info", collect_ask_more_disease_info)
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
        .add_node(
            "request_diagnosis_result_query_node", request_diagnosis_result_query_node
        )
        .add_node(
            "collect_diagnosis_result_query_node", collect_diagnosis_result_query_node
        )
        # End node
        .add_node("end_node", end_node)
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
        .add_edge("process_disease_info", "request_ask_more_disease_info")
        .add_edge("request_ask_more_disease_info", "collect_ask_more_disease_info")
        .add_conditional_edges(
            "collect_ask_more_disease_info",
            route_after_asking_disease_info,
            {"request_disease_info": "request_disease_info", "end_node": "end_node"},
        )
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
        .add_edge("final_refined_diagnosis", "request_diagnosis_result_query_node")
        .add_edge(
            "request_diagnosis_result_query_node", "collect_diagnosis_result_query_node"
        )
        .add_conditional_edges(
            "collect_diagnosis_result_query_node",
            route_diagnosis_result_query_node,
            {"request_disease_info": "request_disease_info", "end_node": "end_node"},
        )
        .add_edge("end_node", END)
    )

    return graph


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
                for state in chunk["data"].values():
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


# with GraphDatabase.driver(URI, auth=AUTH) as driver:
#     # Define your initial state setup
#     run_graph(graph, driver)
