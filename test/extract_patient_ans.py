import json
from typing import List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

class PatientAnswerSchema(BaseModel):
    positive_symptoms: List[str] = Field(
        description="Positive symptoms"
    )
    
    negative_symptoms: List[str] = Field(
        description="Negative symptoms"
    )

parser = PydanticOutputParser(pydantic_object=PatientAnswerSchema)

llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    model="qwen3.5-4b",
    api_key="lm-studio",
    temperature=0,
    reasoning=None
)

prompt_template = """
You are a medical response interpreter.

You will be given:
1. A medical question asked to a patient
2. The patient's answer

Your task is to extract symptoms and classify them into:

- positive_symptoms (symptoms the patient HAS)
- negative_symptoms (symptoms the patient DOES NOT HAVE)
- unknown_symptoms (not clearly stated)

Rules:
- Do NOT add new symptoms
- Use simple normalized symptom phrases
- If answer is "yes", assume all symptoms in the question are present
- If answer is "no", assume all symptoms in the question are absent
- If partially yes, split logically
---
Output Format
{format_instructions}
---
Question:
{question}
---
Patient answer:
{answer}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["question", "answer"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

structured_llm = llm.with_structured_output(PatientAnswerSchema)

classifier_chain = prompt | structured_llm

def extract_patient_ans(question, answer):
    return classifier_chain.invoke({
        "question": json.dumps(question),
        "answer": json.dumps(answer)
    })