import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class SymptomClassifierSchema(BaseModel):
    positive_symptoms: list[str] = Field(
        description="All the positive symptoms described by patient"
    )

    negative_symptoms: list[str] = Field(
        description="All the negative symptoms described by patient"
    )


llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model=os.getenv("LLM_MODEL"),
    api_key="lm-studio",
    temperature=0,
)

prompt_template = """
You are a medical information extraction system.

Your task is to extract and normalize medical symptoms from a patient's free-text response to a medical question for use in a clinical decision support system.

You MUST NOT diagnose the patient.
You MUST ONLY extract and structure symptoms.

---

## INPUT

Asked question:
{question}
---
Patient response:
{input}
---

## TASK

Extract clinically relevant symptoms from the patient's response while considering the relationship between the asked question and the answer.

You must:

1. Identify ALL symptoms mentioned or confirmed through the patient's response.
2. Classify each symptom as either:
   - positive symptom (present in the patient)
   - negative symptom (explicitly denied by the patient)
3. Normalize symptoms into standard clinical terms.

---

## QUESTION-ANSWER INTERPRETATION RULES

The asked question provides context for interpreting the patient's response.

Examples:

Question:
"Do you have fever and runny nose?"

Patient response:
"Yes"

Extract:
- Positive symptoms:
  - fever
  - runny nose

---

Question:
"Do you have fever and runny nose?"

Patient response:
"No"

Extract:
- Negative symptoms:
  - fever
  - runny nose

---

Question:
"Do you have fever and runny nose?"

Patient response:
"I have fever but not runny nose"

Extract:
- Positive symptoms:
  - fever

- Negative symptoms:
  - runny nose

---

Question:
"Are you experiencing chest pain?"

Patient response:
"I don't have any chest pain"

Extract:
- Negative symptoms:
  - chest pain

---

Question:
"Do you have cough, fever, or fatigue?"

Patient response:
"I only have cough"

Extract:
- Positive symptoms:
  - cough

- Negative symptoms:
  - fever
  - fatigue

---

## NORMALIZATION RULES

- Convert colloquial expressions into clinical terms:
  - "peeing a lot" → polyuria
  - "feeling sick" → malaise
  - "pain behind eyes" → retro-orbital pain
  - "body hurts" → myalgia
  - "tired all the time" → fatigue

- Remove filler words (e.g. "really", "very", "kind of", "feels like")
- Merge duplicate or similar symptoms into one canonical term
- Preserve the original symptom meaning after normalization

---

## OUTPUT RULES

Return ONLY structured output in the required format.

- No explanations
- No diagnosis
- No disease names
- No extra text

---

## IMPORTANT RULES

- Do NOT provide diagnosis or disease names
- Do NOT rank diseases
- Do NOT infer unrelated symptoms
- Use the asked question only to resolve whether queried symptoms are present or absent
- If the patient gives a direct answer such as "yes" or "no", map the symptoms from the question accordingly
- If the patient partially confirms or denies symptoms, extract each symptom individually
- Preserve medical neutrality
"""

structured_llm = llm.with_structured_output(
    SymptomClassifierSchema, method="json_schema"
)

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["input", "question"],
)


classifier_chain = prompt | structured_llm


def extract_follow_up_question_symptom(input, question) -> SymptomClassifierSchema:
    return classifier_chain.invoke(
        {
            "input": input,
            "question": question,
        }
    )
