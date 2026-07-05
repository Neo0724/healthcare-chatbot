from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.config import get_stream_writer
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.types import Command, interrupt
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
import os

from app.llm.extract_disease_names import extract_disease_names

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model="qwen3.5-4b",
    api_key="lm-studio",
    temperature=0,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_messages: List[str]
    topic: str
    joke: str


def greet_user(state: State):
    response = llm.invoke([SystemMessage(content="Greet the user")])
    return {"messages": [response]}


def request_permission(state: State):
    response = llm.invoke(
        [SystemMessage(content="Ask if the user want to generate joke")]
    )
    return {"messages": [response]}


def collect_permission(state: State):
    last_message = state["messages"][-1]

    choice = interrupt(last_message)

    return {"user_messages": state["user_messages"] + [choice]}


def generate_joke(state: State):
    response = llm.invoke([SystemMessage(content="Tell user a joke")])
    return {"messages": [response]}


def request_tell_more(state: State):
    response = llm.invoke(
        [SystemMessage(content="Ask the user if he wants more joke")]
    )
    return {"messages": [response]}

def collect_tell_more(state: State):
    last_message = state["messages"][-1]

    choice = interrupt(last_message)

    return {"user_messages": state["user_messages"] + [choice]}

def generate_bye(state: State):
    response = llm.invoke([SystemMessage(content="Say good bye to user")])
    return {"messages": [response]}

# ROUTER
def check_permission(state: State):
    choice = state["user_messages"][-1]

    if "yes" in choice.lower():
        return "generate_joke"
    else:
        return "generate_bye"

def check_tell_more(state: State):
    choice = state["user_messages"][-1]

    if "yes" in choice.lower():
        return "generate_joke"
    else:
        return "generate_bye"


graph = (
    StateGraph(State)
    .add_node(greet_user)
    .add_node(request_permission)
    .add_node(collect_permission)
    .add_node(generate_joke)
    .add_node(request_tell_more)
    .add_node(collect_tell_more)
    .add_node(generate_bye)
    .add_edge(START, "greet_user")
    .add_edge("greet_user", "request_permission")
    .add_edge("request_permission", "collect_permission")
    .add_conditional_edges(
        "collect_permission",
        check_permission,
        {
            "generate_joke": "generate_joke",
            "generate_bye": "generate_bye",
        },
    )
    .add_edge("generate_joke", "request_tell_more")
    .add_edge("request_tell_more", "collect_tell_more")
    .add_conditional_edges(
        "collect_tell_more",
        check_tell_more,
        {
            "generate_joke": "generate_joke",
            "generate_bye": "generate_bye",
        },
    )
    .add_edge("generate_bye", END)
    .compile(checkpointer=InMemorySaver())
)

initial_state = {
    "messages": [],
    "user_messages": [],
    "topic": "",
    "joke": "",
}
config = {"configurable": {"thread_id": "thread-1"}}

while True:
    for chunk in graph.stream(
        initial_state, stream_mode=["updates"], version="v2", config=config
    ):
        if chunk["type"] == "updates":
            print("Update Chunk")
            for node_name, state in chunk["data"].items():
                if "messages" in state:
                    print(f"Updated message: {state['messages']}")
            if "__interrupt__" in chunk["data"]:
                # print(chunk["data"]["__interrupt__"][0].value.content)
                interrupt_value = chunk["data"]["__interrupt__"][0].value.content
                user_input = input(interrupt_value + "\nAnswer: ")
                initial_state = Command(resume=user_input)
    else:
        print("Done")
        break