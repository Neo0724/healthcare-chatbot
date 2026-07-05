import json
from typing import List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "neoben007")

class QuestionItem(TypedDict):
    question: str = Field(
        description="A clinically relevant yes/no or simple diagnostic question."
    )

    reason: str = Field(
        description="Why this question helps differentiate between candidate diseases."
    )

class QuestionsSchema(BaseModel):
    questions: List[QuestionItem] = Field(
        max_length=5,
        description="Up to 5 high-information-gain diagnostic questions."
    )

parser = PydanticOutputParser(pydantic_object=QuestionsSchema)

llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    model="qwen3.5-4b",
    api_key="lm-studio",
    temperature=0,
    reasoning=None
)

prompt_template = """
You are a clinical decision support assistant.

You will be given:
1. A list of possible diseases and their symptom summaries
2. The patient's CURRENTLY KNOWN symptoms (positive symptoms they have)
3. The patient's CURRENTLY ABSENT symptoms (negative symptoms they do NOT have)
4. The questions that have been asked previously (Might be empty if it is the firstly asked question)

Your task is to ask ONE simple, patient-friendly question that helps narrow down the most likely disease.
---
RULES:
- Only use information implied by the disease symptom summaries
- Use the patient's existing positive and negative symptoms to avoid repeating already known information
- Do NOT ask about symptoms that are already confirmed as present or absent
- Do NOT use medical terminology; use simple everyday language
- The question must help differentiate between the possible diseases
- Ask ONLY ONE question
- The question must be answerable with YES or NO
- Keep the question short, clear, and natural for a patient

DISEASES AND SYMPTOM SUMMARIES:
{input}
---
PATIENT KNOWN POSITIVE SYMPTOMS:
{positive_symptoms}
---
PATIENT KNOWN NEGATIVE SYMPTOMS:
{negative_symptoms}
---
ALREADY ASKED QUESTIONS:
{asked_questions}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["input"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# structured_llm = llm.with_structured_output(QuestionsSchema)

classifier_chain = prompt | llm

def get_follow_up_questions(input, positive_symptoms, negative_symptoms, asked_questions):
    return classifier_chain.invoke({
        "input": json.dumps(input),
        "positive_symptoms": json.dumps(positive_symptoms),
        "negative_symptoms": json.dumps(negative_symptoms),
        "asked_questions": json.dumps(asked_questions),
    }).content