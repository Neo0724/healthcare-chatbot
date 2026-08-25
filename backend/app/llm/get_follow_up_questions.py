import json
import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
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

prompt_template = """
You are an expert clinical decision support assistant.

You will be given:
1. POSSIBLE DISEASES: A list of possible diseases and their symptom summaries.
2. POSITIVE SYMPTOMS: Symptoms the patient definitely HAS.
3. NEGATIVE SYMPTOMS: Symptoms the patient definitely does NOT HAVE.
4. ASKED QUESTIONS: Questions already asked in previous turns.

Your objective is to formulate ONE patient-friendly YES/NO question that has the highest clinical value for differentiating between the remaining possible diseases.

---
STRICT RULES:
1. THE EXCLUSION RULE (CRITICAL): You must NEVER ask about a symptom already listed in POSITIVE SYMPTOMS, NEGATIVE SYMPTOMS, or ALREADY ASKED QUESTIONS. 
2. SYNONYM CHECK: Recognize medical and layperson synonyms. If "fatigue" is known, do not ask about "feeling tired." If "fever" is known, do not ask about "feeling hot."
3. MAXIMIZE DISCRIMINATORY POWER: Choose a "pivot symptom"—a specific symptom that strongly rules in one candidate disease while ruling out another. Avoid generic symptoms (like general malaise) that are present in all candidate diseases.
4. PATIENT-FRIENDLY TONE: The `question` must use simple, everyday language (e.g., "Does it hurt when you swallow?" instead of "Are you experiencing odynophagia?").
5. JUSTIFY THE CLINICAL LOGIC: The `reason` field must clearly explain your differential diagnosis logic. It must explicitly state how a YES or a NO answer alters the probabilities of specific candidate diseases.

---
INPUT DATA:
DISEASES AND SYMPTOM SUMMARIES:
{input}

PATIENT KNOWN POSITIVE SYMPTOMS:
{positive_symptoms}

PATIENT KNOWN NEGATIVE SYMPTOMS:
{negative_symptoms}

ALREADY ASKED QUESTIONS:
{asked_questions}
---

OUTPUT FORMAT:
Provide your response strictly as a JSON object with exactly two fields: `reason` and `question`. Do not include markdown code blocks or any outside text.

{{
  "reason": "1. Exclusion Check: Verified chosen symptom is not a synonym of known/asked symptoms. 2. Clinical Logic: Explaining why this pivot symptom helps differentiate Disease A from Disease B based on the predicted impact of a YES vs. NO answer.",
  "question": "Your patient-friendly YES/NO question here."
}}
"""


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
