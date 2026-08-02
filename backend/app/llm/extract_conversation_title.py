import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class ConversationTitleSchema(BaseModel):
    title: str = Field(description="The conversation title")


llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model=os.getenv("LLM_MODEL"),
    api_key="lm-studio",
    temperature=0,
)

prompt_template = """
Based on the user query given below, you are required to extract a suitable conversation title.
---
User Query:
{user_query}
"""

structured_llm = llm.with_structured_output(
    ConversationTitleSchema, method="json_schema"
)

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["user_query"],
)

classifier_chain = prompt | structured_llm


def extract_conversation_title(input: str) -> str:
    result = classifier_chain.invoke({"user_query": input}).title
    return result
