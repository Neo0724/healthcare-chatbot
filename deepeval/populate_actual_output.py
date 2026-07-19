import os
from dotenv import load_dotenv
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from neo4j import Record
import pandas as pd
from pydantic import BaseModel, Field
from sentence_transformers import CrossEncoder

from llm.extract_disease_name import extract_disease_name
from llm.extract_question_scope import extract_question_scope
from output_prompt_template.prompt_template_faithfulness import prompt_template
from db.get_disease_information import get_diseases_information

from llm.custom_llm import CustomLLM
from utils.context_cleaner import clean_context_chunk

load_dotenv()

TEST_SET_FILE = "./synthetic_data/test_set_combined_2_v2.csv"

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

reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")


def generate_response(user_query: str, retrieved_information: List[str]) -> str:
    # 2. Define the RAG prompt template with strict patient-facing instructions
    class OutputSchema(BaseModel):
        response: str = Field(description="Generated response")

    rag_prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["retrieved_information", "query"],
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

    if retrieved_information and len(retrieved_information) > 0:
        # final_prompt = rag_prompt.format(
        #     definition=clean_context_chunk(
        #         "\n".join(retrieved_records[0].data().get("definition"))
        #     ),
        #     symptom=clean_context_chunk(
        #         "\n".join(retrieved_records[0].data().get("symptom"))
        #     ),
        #     treatment=clean_context_chunk(
        #         "\n".join(retrieved_records[0].data().get("treatment"))
        #     ),
        #     query=user_query,
        # )
        final_prompt = rag_prompt.format(
            retrieved_information=retrieved_information,
            query=user_query,
        )

    else:
        # final_prompt = rag_prompt.format(
        #     definition="Not available",
        #     symptom="Not available",
        #     treatment="Not available",
        #     query=user_query,
        # )

        final_prompt = rag_prompt.format(
            retrieved_information="Not available",
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


def rerank_contexts(user_query, contexts):
    pairs = [[user_query, context] for context in contexts]

    scores = reranker.predict(pairs)

    updated_context = sorted(zip(scores, pairs), key=lambda x: x[0], reverse=True)

    cleaned = [context[1][1] for context in updated_context]

    return cleaned[:10]


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

    current_retrieved_context = []

    if len(records) > 0:
        definition = records[0].data().get("definition", [])
        symptom = records[0].data().get("symptom", [])
        treatment = records[0].data().get("treatment", [])

        current_retrieved_context.extend(
            clean_context_chunk(str(d)) for d in definition
        )
        current_retrieved_context.extend(clean_context_chunk(str(s)) for s in symptom)
        current_retrieved_context.extend(clean_context_chunk(str(t)) for t in treatment)

    reranked_context = rerank_contexts(
        user_query=user_query, contexts=current_retrieved_context
    )

    reranked_context_str = "\n[context_seperator]\n".join(c for c in reranked_context)

    # Generate answer
    actual_output = generate_response(user_query, "\n".join(reranked_context))

    actual_outputs.append(actual_output)
    retrieved_contexts.append(reranked_context_str)

# Add/overwrite columns
df["actual_output"] = actual_outputs
df["retrieved_context"] = retrieved_contexts

# Save to new file with "_populated" suffixpopulate_ac
base, ext = os.path.splitext(input_csv)
output_csv = f"{base}_populated{ext}"

df.to_csv(output_csv, index=False)

print(f"\n✅ Populated dataset saved to: {output_csv}")
