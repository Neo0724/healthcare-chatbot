import os
from dotenv import load_dotenv
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from neo4j import Record
import pandas as pd
from pydantic import BaseModel, Field

from llm.extract_disease_name import extract_disease_name
from llm.extract_question_scope import extract_question_scope
from output_prompt_template.prompt_template_faithfulness import prompt_template
from db.get_disease_information import get_diseases_information

from llm.custom_llm import CustomLLM
from utils.context_cleaner import clean_context_chunk

load_dotenv()

TEST_SET_FILE = "./synthetic_data/test_set_8.csv"

# custom_llm = CustomLLM(
#     model=ChatOpenAI(
#         base_url=os.getenv("LLM_URL"),
#         model="meta-llama-3.1-8b-instruct",
#         api_key="lm-studio",
#         temperature=0.2,
#         frequency_penalty=1.0,
#         presence_penalty=0.6,
#         max_completion_tokens=5000,
#         extra_body={
#             "repetition_penalty": 1.15,
#             "top_p": 0.9,
#         },
#     ),
#     model_name="meta-llama-3.1-8b-instruct",
# )

custom_llm = CustomLLM(
    model=ChatOpenAI(
        base_url=os.getenv("LLM_URL"),
        model=os.getenv("LLM_MODEL"),
        api_key="lm-studio",
        temperature=0.2,
        frequency_penalty=1.0,
        presence_penalty=0.6,
        max_completion_tokens=5000,
        extra_body={
            "repetition_penalty": 1.15,
            "top_p": 0.95,
            "top_k": 20,
            "min_p": 0.0,
        },
    ),
    model_name="qwen3-14b",
)


def generate_response(user_query: str, retrieved_records: List[Record]) -> str:
    # 2. Define the RAG prompt template with strict patient-facing instructions
    class OutputSchema(BaseModel):
        response: str = Field(description="Generated response")

    rag_prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["definition", "symptom", "treatment", "query"],
    )

    llm = ChatOpenAI(
        base_url=os.getenv("LLM_URL"),
        model=os.getenv("LLM_MODEL"),
        api_key="lm-studio",
        temperature=0.2,
        frequency_penalty=1.0,
        presence_penalty=0.6,
        max_completion_tokens=5000,
        extra_body={
            "repetition_penalty": 1.15,
            "top_p": 0.95,
            "top_k": 20,
            "min_p": 0.0,
        },
    )

    structured_llm = llm.with_structured_output(OutputSchema, method="json_schema")

    # 3. Format the inputs into the prompt string
    # Convert your Neo4j records/dictionaries into a clean string layout for the LLM context block

    if retrieved_records and len(retrieved_records) > 0:
        final_prompt = rag_prompt.format(
            definition=clean_context_chunk(
                "\n".join(retrieved_records[0].data().get("definition"))
            ),
            symptom=clean_context_chunk(
                "\n".join(retrieved_records[0].data().get("symptom"))
            ),
            treatment=clean_context_chunk(
                "\n".join(retrieved_records[0].data().get("treatment"))
            ),
            query=user_query,
        )

    else:
        final_prompt = rag_prompt.format(
            definition="Not available",
            symptom="Not available",
            treatment="Not available",
            query=user_query,
        )

    # 4. Generate the final answer using your local model wrapper
    # Note: Using .generate() since your CustomLLM handles strings directly
    try:
        print("Generating actual output ...")
        result = structured_llm.invoke(final_prompt)
        print(f"Finished generating actual output:\n{result.response}\n")
        return result.response.strip()
    except Exception as e:
        print(f"⚠️ Error generating RAG pipeline response: {e}")
        return "I am sorry, I am having trouble accessing the database information right now."


# Load dataset
input_csv = TEST_SET_FILE
df = pd.read_csv(input_csv)

# Create lists to store results
actual_outputs = []
retrieved_contexts = []

print("⏳ Gathering actual outputs from your live RAG system...")

for index, row in df.iterrows():
    print(f"Processing test set no: {index + 1}")
    print(f"Given input: {row['input']}")

    user_query = row["input"]

    extracted_disease_name = extract_disease_name(user_query)
    # scopes = extract_question_scope(user_query)
    records = get_diseases_information(
        extracted_disease_name, ["Definition", "Symptoms", "Treatment"]
    )

    retrieved_context = []

    if len(records) > 0:
        definition = records[0].data().get("definition", [])
        symptom = records[0].data().get("symptom", [])
        treatment = records[0].data().get("treatment", [])

        retrieved_context.extend(definition)
        retrieved_context.extend(symptom)
        retrieved_context.extend(treatment)

    # String version for CSV
    retrieved_context_str = "\n".join(
        clean_context_chunk(str(c)) for c in retrieved_context
    )

    # Generate answer
    actual_output = generate_response(user_query, records)

    actual_outputs.append(actual_output)
    retrieved_contexts.append(retrieved_context_str)

# Add/overwrite columns
df["actual_output"] = actual_outputs
df["retrieved_context"] = retrieved_contexts

# Save to new file with "_populated" suffix
base, ext = os.path.splitext(input_csv)
output_csv = f"{base}_populated{ext}"

df.to_csv(output_csv, index=False)

print(f"\n✅ Populated dataset saved to: {output_csv}")
