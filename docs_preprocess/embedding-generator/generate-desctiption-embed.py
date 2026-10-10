import logging
import os
import subprocess
import time

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from neo4j import GraphDatabase

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

load_dotenv()

URI = os.getenv("NEO4J_URL")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

# Create embedding model
embeddings_model = HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-base-v0.1")

logging.basicConfig(
    filename="logs/embed.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def count_total_description_nodes(driver):
    records, _, _ = driver.execute_query(
        """
        MATCH (d:Description)
        RETURN count(d) as totalNodes
        """,
        database_="neo4j",
    )

    return records[0]["totalNodes"]


def shutdown():
    subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", r".\shutdown-neo4j.ps1"],
        check=True,
    )


def batch_process_embedding(driver, total_nodes):
    # Process 250 descriptions at once
    BATCH_SIZE = 850

    # counter = 0
    counter = 655900

    while counter < total_nodes:
        records, _, _ = driver.execute_query(
            """ 
            MATCH (d:Description)
            RETURN d.id, d.term 
            ORDER BY d.id
            SKIP $counter LIMIT $batch_size
            """,
            counter=counter,
            batch_size=BATCH_SIZE,
        )

        ids = [r["d.id"] for r in records]
        terms = [r["d.term"] for r in records]

        embeddings = embeddings_model.embed_documents(terms)

        batch_updates = [{"id": i, "embedding": e} for i, e in zip(ids, embeddings)]

        # Batch write
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (d:Description {id: row.id})
            SET d.embedding = vector(row.embedding, 768, FLOAT)
            """,
            batch=batch_updates,
        )

        print(f"Batch done: {counter + BATCH_SIZE}")
        logging.info(f"Batch done: {counter + BATCH_SIZE}")
        counter += BATCH_SIZE


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    start_time = time.perf_counter()

    total_nodes = count_total_description_nodes(driver)
    batch_process_embedding(driver, total_nodes)

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    logging.info("Finished adding embeddings!")
    logging.info(f"Execution time: {execution_time:.6f} seconds")
    logging.info("Shutting down PC......")
    shutdown()
