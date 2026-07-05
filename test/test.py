import logging
from typing import List

from extract_medical_entities import extract_medical_entities
from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from neo4j import GraphDatabase
import numpy as np
from pydantic import BaseModel, Field
import os

import extract_patient_ans
from llm import get_follow_up_questions

logging.basicConfig(
    filename="test.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "neoben007")

embeddings_model = HuggingFaceEmbeddings(
    model_name="abhinand/MedEmbed-base-v0.1"
)

# model = CrossEncoder("Qwen/Qwen3-Reranker-0.6B")

def get_possible_diseases(driver, positive_embedding, negative_embedding):
    records, _, _ = driver.execute_query(
        """
        CALL() {
            MATCH (s:Symptoms)
            SEARCH s IN (
                VECTOR INDEX `symptom_embed`
                FOR vector($positive_embedding, 768, FLOAT NOT NULL)
                LIMIT 50
            ) SCORE AS score
            MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(s)
            WHERE s.disease_category <> "SURGERY"
            RETURN o as post_nodes, score as post_score
        }

        CALL()  {
            MATCH (s:Symptoms)
            SEARCH s IN (
                VECTOR INDEX `symptom_embed` 
                FOR vector($negative_embedding, 768, FLOAT)
                LIMIT 50
            ) SCORE as score
            MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(s)
            RETURN o as neg_nodes, score as neg_score
        }

        WITH post_nodes, post_score, collect(elementId(neg_nodes)) as neg_nodes_ids
        
        WHERE NOT elementId(post_nodes) IN neg_nodes_ids

        AND (
            post_nodes.FSN CONTAINS "(disorder)"
            OR
            post_nodes.FSN CONTAINS "(finding)"
        )

        MATCH (post_nodes)-[:HAS_RESOURCE]->(sym:Symptoms)

        RETURN DISTINCT post_nodes.FSN as disease_name, post_nodes.id as disease_id, max(post_score) as post_score, collect(sym.summary) as symptom_summary

        ORDER BY post_score DESC

        LIMIT 10
        """,
        database_="neo4j",
        positive_embedding=positive_embedding,
        negative_embedding=negative_embedding
    )

    return records

def narrow_down(driver, positive_embedding, negative_embedding, initial_ids):
    records, _, _ = driver.execute_query(
        """
        CALL() {
            MATCH (s:Symptoms)
            SEARCH s IN (
                VECTOR INDEX `symptom_embed`
                FOR vector($positive_embedding, 768, FLOAT NOT NULL)
                LIMIT 50
            ) SCORE AS score
            MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(s)
            WHERE s.disease_category <> "SURGERY"
            RETURN o as post_nodes, score as post_score
        }

        CALL()  {
            MATCH (s:Symptoms)
            SEARCH s IN (
                VECTOR INDEX `symptom_embed` 
                FOR vector($negative_embedding, 768, FLOAT)
                LIMIT 50
            ) SCORE as score
            MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(s)
            RETURN o as neg_nodes, score as neg_score
        }

        WITH post_nodes, post_score, collect(elementId(neg_nodes)) as neg_nodes_ids
        
        WHERE NOT elementId(post_nodes) IN neg_nodes_ids

        AND (
            post_nodes.FSN CONTAINS "(disorder)"
            OR
            post_nodes.FSN CONTAINS "(finding)"
        )

        MATCH (post_nodes)-[:HAS_RESOURCE]->(sym:Symptoms)

        WHERE post_nodes.id in $initial_ids

        RETURN DISTINCT post_nodes.FSN as disease_name, post_nodes.id as disease_id, max(post_score) as post_score, collect(sym.summary) as symptom_summary

        ORDER BY post_score DESC

        LIMIT 10
        """,
        database_="neo4j",
        positive_embedding=positive_embedding,
        negative_embedding=negative_embedding,
        initial_ids=initial_ids
    )

    return records

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    initial_input = "I have a fever, chills, and vomiting. I also have a headache, and I've been sweating a lot. I also feel nauseous and have muscle aches."

    extracted_entities = extract_medical_entities(initial_input)

    positive_symptoms = extracted_entities.positive_symptoms
    negative_symptoms = extracted_entities.negative_symptoms

    positive_embedding = embeddings_model.embed_query(",".join(positive_symptoms))
    negative_embedding = embeddings_model.embed_query(",".join(negative_symptoms))

    records = get_possible_diseases(driver, positive_embedding, negative_embedding)

    initial_ids = []

    # documents = [record.get("disease_name", "") for record in records]
    # rankings = model.rank(positive_symptoms, documents)
    # scored = [
    #     (documents[r["corpus_id"]], r["score"])
    #     for r in rankings
    # ]

    # scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)

    # for index, (doc, score) in enumerate(scored_sorted):
    #     logging.info(f"Rank: {index + 1} | FSN: {doc} | Reranked Score: {score}")

    for index, record in enumerate(records):
        initial_ids.append(record.get('disease_id', ''))
        logging.info(f"Rank: {index + 1} | FSN: {record.get("disease_name", "")} | Score: {record.get("post_score", ""):.4f} | Summary: {record.get("symptom_summary", [])}")
        print(f"Rank: {index + 1} | FSN: {record.get("disease_name", "")} | Score: {record.get("post_score", ""):.4f}")

    disease_summary = {
        "questions": [
            {
                "disease_name": r.get("disease_name", ""),
                "symptom": r.get("symptom_summary", []),
            } for r in records
        ]
    }

    asked_questions = []

    for i in range(10):
        logging.info(f"Question {i}\n")
        response = get_follow_up_questions(disease_summary, positive_symptoms, negative_symptoms, asked_questions)

        asked_questions.append(response)

        logging.info(f"Question:\n\n {response}")
        print(f"Question:\n{response}")

        patient_input = input("Answer: ")

        patient_response = extract_patient_ans.extract_patient_ans(response, patient_input)

        logging.info(f"Initial Positive Symptoms: {positive_symptoms}")
        logging.info(f"Initial Negative Symptoms: {negative_symptoms}")

        logging.info(f"New Positive Symptoms: {patient_response.positive_symptoms}")
        logging.info(f"New Negative Symptoms: {patient_response.negative_symptoms}")

        # Updated
        positive_symptoms += patient_response.positive_symptoms
        negative_symptoms += patient_response.negative_symptoms

        logging.info(f"Final: Positive Symptoms: {positive_symptoms}")
        logging.info(f"Final: Negative Symptoms: {negative_symptoms}")

    positive_embedding = embeddings_model.embed_query(",".join(positive_symptoms))
    negative_embedding = embeddings_model.embed_query(",".join(negative_symptoms))

    records = narrow_down(driver, positive_embedding, negative_embedding, initial_ids)

    logging.info("UPDATED:\n")
    for index, record in enumerate(records):
        logging.info(f"Rank: {index + 1} | FSN: {record.get("disease_name", "")} | Score: {record.get("post_score", ""):.4f} | Summary: {record.get("symptom_summary", [])}")
        print(f"Rank: {index + 1} | FSN: {record.get("disease_name", "")} | Score: {record.get("post_score", ""):.4f}")

    # for q in response.questions:
    #     print(q)
    #     logging.info(f"Question: {q.get("question", "")} | Reason: {q.get("reason", "")}")


    # positive_embeddings = [embeddings_model.embed_query(symptom) for symptom in positive_symptoms]
    # negative_embeddings = [embeddings_model.embed_query(symptom) for symptom in negative_symptoms]

    # final(driver, positive_embeddings, negative_embeddings)
