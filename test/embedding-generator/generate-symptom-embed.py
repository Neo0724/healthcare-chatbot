from langchain_huggingface import HuggingFaceEmbeddings
import os
from neo4j import GraphDatabase
import logging
import time
import subprocess

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "neoben007")

# Create embedding model
# https://arxiv.org/abs/2412.15258
embeddings_model = HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-base-v0.1")

logging.basicConfig(
    filename="logs/symptom-embed.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",  
)


def count_total_symptom_nodes(driver):
    records, _, _ = driver.execute_query(
        """
        MATCH (mr:Symptoms)
        WHERE mr.embedding IS NULL
        RETURN count(mr) as totalNodes
        """,
        database_="neo4j",
    )

    return records[0]["totalNodes"]


def batch_process_embedding(driver, total_nodes):
    # Process 50 descriptions at once
    BATCH_SIZE = 50

    counter = 0

    while counter < total_nodes:
        records, _, _ = driver.execute_query(
            """ 
            MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(mr:Symptoms)
            WHERE mr.embedding IS NULL
            RETURN elementId(mr) as mr_id, mr.summary as summary, mr.tags as tags, o.FSN as disease_name
            ORDER BY elementId(mr)
            LIMIT $batch_size
            """,
            batch_size=BATCH_SIZE,
        )

        ids = [r["mr_id"] for r in records]

        summary_to_embed = [
            f"Disease: {r.get("disease_name", "")} | Summary: {r.get("summary", "")} | Tags: {", ".join(r.get("tags", [])[:8])}"
            for r in records
        ]

        embeddings = embeddings_model.embed_documents(summary_to_embed)    

        batch_updates = [
            {
                "id": id,
                "embedding": embedding
            } for id, embedding in zip(ids, embeddings)
        ]

        # Batch write
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (mr:Symptoms)
            WHERE elementId(mr) = row.id
            SET mr.embedding = vector(row.embedding, 768, FLOAT)
            """,
            batch=batch_updates,
        )

        print(f"Batch done: {counter + BATCH_SIZE}")
        logging.info(f"Batch done: {counter + BATCH_SIZE}")
        counter += BATCH_SIZE

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    start_time = time.perf_counter()

    total_nodes = count_total_symptom_nodes(driver)
    batch_process_embedding(driver, total_nodes)

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    logging.info("Finished adding embeddings!")
    logging.info(f"Execution time: {execution_time:.6f} seconds")