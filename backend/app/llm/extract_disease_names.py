from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()


class DiseaseNameClassifierSchema(BaseModel):
    medical_entities: List[str] = Field(
        description="All the stated disease name by user"
    )


parser = PydanticOutputParser(pydantic_object=DiseaseNameClassifierSchema)

llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model="qwen3.5-4b",
    api_key="lm-studio",
    temperature=0,
    reasoning=None,
)

prompt_template = """
You are a strict medical entity extraction system.

Your task:
Extract ONLY medically relevant entities explicitly mentioned by the user.

Entities include:
- Diseases (e.g., diabetes, dengue, influenza)
- Symptoms (e.g., fever, cough, sore throat, headache)

Rules:
1. Only extract entities explicitly mentioned in the user input.
2. Do NOT infer, diagnose, or predict conditions.
3. Do NOT add any medical entities that are not explicitly stated.
4. Do NOT extract treatments, medications, anatomy, or general health advice.
5. Preserve original wording as much as possible.
6. Remove duplicates.
7. If no valid medical entity is found, return an empty list.
8. Do NOT classify, explain, or group entities.
9. Output ONLY valid structured JSON matching the schema. No extra text.
---
{format_instructions}
---
User input:
{input}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["input"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

structured_llm = llm.with_structured_output(DiseaseNameClassifierSchema)

classifier_chain = prompt | structured_llm


def extract_disease_names(input) -> List[str]:
    return classifier_chain.invoke({"input": input}).medical_entities
