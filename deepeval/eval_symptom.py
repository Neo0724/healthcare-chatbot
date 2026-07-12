import os
from dotenv import load_dotenv
from datetime import datetime
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
import pandas as pd
from db.get_possible_diseases import get_possible_diseases
from llm.custom_llm import CustomLLM
from llm.extract_symptoms import extract_symptoms

load_dotenv()

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"

embeddings_model = HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-base-v0.1")

FILENAME = "./synthetic_data/symptom_test_set_v5.csv"

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
            "top_p": 0.85,
            "top_k": 20,
            "min_p": 0.05,
        },
    ),
    model_name="qwen3-14b",
)

df = pd.read_csv(FILENAME)

test_cases = []
res = []

for index, row in df.iterrows():
    user_query = row["input"]

    print(f"Processing set **{index + 1}**")

    # print(f"User Input:\n{user_query}")

    extracted_entities = extract_symptoms(user_query)

    # print(f"Extracted Entities:\n {extracted_entities}")

    positive_symptoms = list(extracted_entities.positive_symptoms)
    negative_symptoms = list(extracted_entities.negative_symptoms)

    positive_embedding = embeddings_model.embed_query(",".join(positive_symptoms))
    negative_embedding = embeddings_model.embed_query(",".join([]))

    records = get_possible_diseases(
        negative_embedding=negative_embedding, positive_embedding=positive_embedding
    )

    # retrieved_symptom_contexts = [
    #     "\n".join(r.data().get("symptoms", [])) for r in records
    # ]

    # print(f"Actual disease: {row['source_file']}")
    # print("Retrieved symptom contexts:\n")
    # for r in records:
    #     print(f"Matched: {r.data().get('disease_name', '')}")

    res.append(
        {
            "input": row["input"],
            "disease_name": row["source_file"],
            "found": [r.data().get("disease_name") for r in records],
            "matched": 1
            if row["source_file"] in [r.data().get("disease_name", "") for r in records]
            else 0,
        }
    )

with open(
    f"./symptom_results/test_run_hit_at_10{datetime.now().strftime('%Y%m%d_%H_%M_%S')}.json",
    "w",
    encoding="utf-8",
) as f:
    cur_res = {
        "metric": "Symptom-Disease Hit@10",
        "testCases": {
            "results": res,
            "final_results": {
                "total_test_cases": len(res),
                "total_matched": sum([r.get("matched", 0) for r in res]),
                "total_unmatched": len(res) - sum([r.get("matched", 0) for r in res]),
                "matched_percentage": (
                    sum([r.get("matched", 0) for r in res]) / len(res)
                ),
            },
        }
    }

    json.dump(cur_res, f, indent=4)
