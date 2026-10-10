import json
import logging
import os
import subprocess
import time

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from neo4j import GraphDatabase
from pydantic import BaseModel, Field

load_dotenv()

URI = os.getenv("NEO4J_URL")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

logging.basicConfig(
    filename="definition-summary.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class DefinitionSummarySchema(BaseModel):
    summary: str = Field(
        description="One-sentence concise medical summary of the definition"
    )


parser = PydanticOutputParser(pydantic_object=DefinitionSummarySchema)

llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="qwen3.5-4b",
    temperature=0,
)

prompt_template = """
You are a medical knowledge compression system.

Your task is to convert a disease definition into a single concise sentence that preserves only the clinically essential meaning.

INPUT:
Definition: {definition}
Metadatas (If any): {metadatas}

OUTPUT REQUIREMENTS:
- Write exactly ONE sentence.
- Focus only on clinically relevant meaning.
- Include:
  • core disease nature (what kind of disorder it is)
  • primary mechanism or system involved (if present)
  • key hallmark features or symptoms (only the most characteristic ones)
- Do NOT include:
  • citations, history, epidemiology
  • redundant wording or repetition
  • excessive qualifiers
  • treatment details unless essential to identity
- Avoid lists; integrate information naturally into one sentence.
- Prefer clarity over completeness.
- If multiple features exist, prioritize the most diagnostic ones.

STYLE:
- Clinically accurate
- Neutral tone
- Compact but informative
- Suitable for use in a medical decision-support system

EXAMPLE OUTPUT FORMAT:
"A chronic metabolic disorder characterized by insulin deficiency or resistance leading to persistent hyperglycemia with symptoms such as excessive urination, thirst, and weight loss."

Now generate the summary.
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["definition", "metadatas"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

structured_llm = llm.with_structured_output(DefinitionSummarySchema)

classifier_chain = prompt | structured_llm


def shutdown():
    subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", r".\shutdown-neo4j.ps1"],
        check=True,
    )


def restart_llm_model():
    subprocess.run(["lms", "unload", "qwen3.5-4b"])
    subprocess.run(["lms", "load", "qwen3.5-4b"])


def count_total_definition_nodes(driver):
    records, _, _ = driver.execute_query(
        """
        MATCH (d:Definition)
        RETURN count(d) as totalNodes
        """,
        database_="neo4j",
    )

    return records[0]["totalNodes"]


def generate_symptom_definition(metadatas):
    try:
        logging.info(f"Generating definition summary | metadata={metadatas}")
        parsed_result = classifier_chain.invoke(
            {
                "definition": metadatas.get("content", ""),
                "metadatas": json.dumps(
                    {
                        "disease_category": metadatas.get("disease_category", ""),
                        "disease_name": metadatas.get("disease_name", ""),
                    },
                    ensure_ascii=False,
                ),
            }
        )

        summary = parsed_result.summary

        logging.info(f"Summary generated successfully | summary='{summary}'")

        return {"summary": summary}

    except Exception as e:
        logging.error(f"Error generating symptom summary: {e}")
        return {"summary": ""}


def batch_process_definition_summary(driver, total_nodes):
    # Read and write 50 symptom summary at once
    BATCH_SIZE = 50

    counter = 0

    while counter < total_nodes:
        records, _, _ = driver.execute_query(
            """ 
            MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(mr:Definition)
            WHERE mr.summary IS NULL
            RETURN elementId(mr) as mr_id, mr.content, mr.disease_category, mr.disease_name
            ORDER BY o.id
            SKIP $counter LIMIT $batch_size
            """,
            database="neo4j",
            counter=counter,
            batch_size=BATCH_SIZE,
        )

        definition_ids = [r["mr_id"] for r in records]
        definition_metadatas = [
            {
                "content": r.get("mr.content", ""),
                "disease_category": r.get("mr.disease_category", ""),
                "disease_name": r.get("mr.disease_name", ""),
            }
            for r in records
        ]

        summarized_definition = []

        for i, metadata in enumerate(definition_metadatas):
            if i % 10 == 0:
                restart_llm_model()
            logging.info(f"Processing batch no: {counter} | item no: {i}")
            print(f"Processing batch no: {counter} | item no: {i}")
            summarized_definition.append(generate_symptom_definition(metadata))

        paired_summary = [
            {
                "id": id,
                "summary": s.get("summary", ""),
            }
            for id, s in zip(definition_ids, summarized_definition)
        ]

        # Batch write
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (mr:Definition)
            WHERE elementId(mr) = row.id
            SET mr.summary = row.summary
            """,
            database="neo4j",
            batch=paired_summary,
        )

        print(f"Batch done: {counter + BATCH_SIZE}")
        logging.info(f"Batch done: {counter + BATCH_SIZE}")
        counter += BATCH_SIZE


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    start_time = time.perf_counter()

    total_nodes = count_total_definition_nodes(driver)
    batch_process_definition_summary(driver, total_nodes)

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    logging.info("Finished generating definition summary!")
    logging.info(f"Execution time: {execution_time:.6f} seconds")
    # logging.info("Shutting down PC......")
    # shutdown()
