from typing import List, Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class QuestionScopeClassifier(BaseModel):
    scopes: List[Literal["Definition", "Symptoms", "Treatment"]] = Field(
        description="The extracted medical intent scope(s). Must strictly be one or more of: 'Definition', 'Symptoms', 'Treatment'."
    )


llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    model="qwen3-14b",
    api_key="lm-studio",
    temperature=0,
)

prompt_template = """
You are a strict medical intent classification system.

Your task is to classify all relevant categories of medical information the user is asking about.

Rules:
- You MUST categorize the user's intent using ONLY the following strings:
  "Definition", "Symptoms", or "Treatment".
- You may output ONE OR MORE categories.
- If the input covers multiple categories, include all relevant categories.
- Do NOT output explanations, reasoning, or extra text.
- Output must be a JSON array containing only category names.

Mapping guide:
  * "Definition": Use this if the user asks about what a disease is, its causes, etiology, clinical description, or diagnosis.
  * "Symptoms": Use this if the user asks about signs, clinical features, presentation, characteristics, or how a disease manifests.
  * "Treatment": Use this if the user asks about management, medications, drugs, therapy, IV regimens, or how to cure/alleviate a condition.

Output format:
Return ONLY a JSON array.

Examples:

Input:
What is the clinical description of hypertension regarding its diagnosis?
Output:
["Definition"]

Input:
How is diabetes mellitus managed in adults?
Output:
["Treatment"]

Input:
What are the warning signs and presentation of lung cancer?
Output:
["Symptoms"]

Input:
What are the symptoms of heart failure and how is it treated?
Output:
["Symptoms", "Treatment"]

Input:
What causes infective endocarditis and what are the symptoms?
Output:
["Definition", "Symptoms"]

---
Now extract the category from the following input:

{input}
"""

structured_llm = llm.with_structured_output(
    QuestionScopeClassifier, method="json_schema"
)

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["input"],
)

classifier_chain = prompt | structured_llm


def extract_question_scope(input) -> str:
    print("Extracting scopes ...")
    result = classifier_chain.invoke({"input": input}).scopes
    print(f"Extracted scoprs: **{result}**")
    return result
