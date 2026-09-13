import json
import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from prompt_templates.generate_follow_up_question_prompt import prompt_template
from pydantic import BaseModel, Field

load_dotenv()


class QuestionItem(BaseModel):
    question: str = Field(
        description="A clinically relevant yes/no or simple diagnostic question."
    )

    reason: str = Field(
        description="Why this question helps differentiate between candidate diseases."
    )


llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model=os.getenv("LLM_MODEL"),
    api_key="lm-studio",
    temperature=0,
    reasoning=None,
)


structured_llm = llm.with_structured_output(QuestionItem, method="json_schema")

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=[
        "input",
        "positive_symptoms",
        "negative_symptoms",
        "asked_questions",
    ],
)

classifier_chain = prompt | structured_llm


def get_follow_up_questions(
    input, positive_symptoms, negative_symptoms, asked_questions
):
    return classifier_chain.invoke(
        {
            "input": json.dumps(input),
            "positive_symptoms": json.dumps(positive_symptoms),
            "negative_symptoms": json.dumps(negative_symptoms),
            "asked_questions": asked_questions,
        }
    )
