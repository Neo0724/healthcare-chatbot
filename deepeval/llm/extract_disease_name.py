import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class DiseaseNameClassifierSchema(BaseModel):
    extracted_disease_name: str = Field(description="The extracted disease name")


llm = ChatOpenAI(
    base_url=os.getenv("LLM_URL"),
    model=os.getenv("LLM_MODEL"),
    api_key="lm-studio",
    temperature=0,
)

prompt_template = """

You are a medical information extraction system.

Your task is to extract ONLY the single main disease name mentioned or implied in the user input.

Rules:

- Extract only 1 disease (the primary condition being asked about).
- Do NOT include symptoms, treatments, organs, or general medical terms.
- Do NOT explain anything.
- Do NOT return multiple diseases.
- If multiple diseases appear, choose the main focus of the question.
- PRESERVE SPECIFICITY: If the question names a specific subtype, severity level, complication, or variant of a condition (e.g. "hypertensive emergency", "hypertensive urgency", "gestational hypertension", "type 2 diabetes"), you MUST extract that exact specific name. NEVER collapse it into the broader parent condition (e.g. "hypertensive emergency" must NOT become "hypertension"; "type 2 diabetes" must NOT become "diabetes"). The specific term is a DIFFERENT, more precise clinical entity than its parent — treat them as different diseases.
- NORMALIZE ONLY COLLOQUIAL PHRASING, NOT SPECIFICITY: Normalization means converting informal/lay language into its standard medical name for the SAME condition (e.g. "high blood pressure" → "hypertension", "heart attack" → "myocardial infarction"). It does NOT mean simplifying a specific named subtype down to a general category. If the input already uses a specific medical term, output that term unchanged.
- If no clear disease is present, return "None".
- Only output string NOT list

Output format:

Return only the disease name. No extra text.

Examples:

Input:
What is the clinical description of hypertension regarding its diagnosis and symptoms?
Output:
hypertension

Input:
What defines a hypertensive emergency in adults with BP >180/120 mmHg and potential for acute stroke or organ damage?
Output:
hypertensive emergency

Input:
What is the treatment for hypertensive urgency without signs of organ damage?
Output:
hypertensive urgency

Input:
How is diabetes mellitus treated in adults?
Output:
diabetes mellitus

Input:
What is the recommended insulin regimen for type 2 diabetes?
Output:
type 2 diabetes

Input:
What are the symptoms of lung cancer and how is it diagnosed?
Output:
lung cancer

Input:
What causes headaches after lack of sleep?
Output:
None

---

Now extract the disease from the following input:

{input}

"""

structured_llm = llm.with_structured_output(
    DiseaseNameClassifierSchema, method="json_schema"
)

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["input"],
)

classifier_chain = prompt | structured_llm


def extract_disease_name(input) -> str:
    print("Extracting disease name ...")
    result = classifier_chain.invoke({"input": input}).extracted_disease_name
    print(f"Extracted disease name: **{result}**")
    return result
