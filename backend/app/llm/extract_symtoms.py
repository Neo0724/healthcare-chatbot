from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()


class SymptomClassifierSchema(BaseModel):
    positive_symptoms: List[str] = Field(
        description="All the positive symptoms described by patient"
    )

    negative_symptoms: List[str] = Field(
        description="All the negative symptoms described by patient"
    )


parser = PydanticOutputParser(pydantic_object=SymptomClassifierSchema)

llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model="qwen3.5-4b",
    api_key="lm-studio",
    temperature=0,
    reasoning=None,
)

prompt_template = """
You are a medical information extraction system.

Your task is to extract and normalize medical symptoms from a patient’s free-text description for use in a clinical decision support system.

You MUST NOT diagnose the patient.
You MUST ONLY extract and structure symptoms.

{format_instructions}

---

## INPUT
Patient text:
\"\"\"
{input}
\"\"\"
---

## TASK

Extract clinically relevant symptoms and convert them into a structured format suitable for medical retrieval and embedding.

You must:

1. Identify ALL symptoms mentioned in the text.
2. Classify each symptom as either:
   - positive symptom (present in the patient)
   - negative symptom (explicitly denied by the patient)
3. Normalize symptoms into standard clinical terms.

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
- Do NOT infer symptoms that are not explicitly or clearly implied
- Preserve medical neutrality
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["input"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

structured_llm = llm.with_structured_output(SymptomClassifierSchema)

classifier_chain = prompt | structured_llm


def extract_medical_entities(input):
    return classifier_chain.invoke(
        {
            "input": input,
        }
    )
