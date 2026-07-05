import logging

from app.llm.extract_disease_names import extract_disease_names
# from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from neo4j import GraphDatabase
import os

from app.graph_queries.queries import get_diseases_information

logging.basicConfig(
    filename="test2.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "1"
os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "neoben007")

embeddings_model = HuggingFaceEmbeddings(
    model_name="abhinand/MedEmbed-base-v0.1"
)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    initial_input = "I want to know about asthma, diabetes, malaria"

    extracted_disease_names = extract_disease_names(initial_input)

    print(extracted_disease_names)

    embedding = [embeddings_model.embed_query(d) for d in extracted_disease_names]

    records = get_diseases_information(driver, extracted_disease_names, embedding)

    for r in records:
        print(f"Name: {r.get("disease_name")} | Score: {r.get("score")} | Definitions: {r.get("definitions", [])}\n")