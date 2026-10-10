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
    filename="logs/symptom-summary.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class SymptomSummarySchema(BaseModel):
    summary: str = Field(
        description="One-sentence concise medical summary of the symptom"
    )

    core_symptoms: list[str] = Field(description="Core symptoms")

    secondary_symptoms: list[str] = Field(description="Core symptoms")

    severe_symptoms: list[str] = Field(description="Core symptoms")

    tags: list[str] = Field(
        description="List of key medical keywords or concepts related to the symptom (e.g., 'urination', 'endocrine', 'diabetes')"
    )


parser = PydanticOutputParser(pydantic_object=SymptomSummarySchema)

llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="qwen3.5-4b",
    temperature=0,
)

prompt_template = """
You are a medical knowledge compression assistant.

Your task is to convert a patient symptom description into a structured representation for use in a clinical retrieval and ranking system.

IMPORTANT RULES:
1. Do NOT diagnose any disease.
2. Do NOT introduce new medical facts not present or strongly implied in the input.
3. Do NOT infer causes or conditions.
4. Only reorganize and extract symptom information.
5. Keep all outputs concise (medical keywords only, no sentences in lists).

You MUST extract and organize symptoms into the following structure:

---

1. core_symptoms
- Most important, distinctive, or high-signal symptoms
- Strong indicators of abnormal physiology
- Symptoms that significantly define the clinical picture

2. secondary_symptoms
- Common accompanying symptoms
- Non-specific but clinically relevant
- Moderate importance for pattern matching

3. severe_symptoms
- High-risk, red-flag, or severe manifestations
- May indicate serious or urgent conditions
- Include only if explicitly mentioned or strongly implied

4. summary
- One-sentence neutral medical summary of the symptom presentation
- Must NOT imply diagnosis or disease

5. tags
- Short medical keywords extracted from the input
- No sentences
- No categorization labels

---

STRICT RULES:
- Each symptom must appear in ONLY ONE category
- If uncertain, prefer SECONDARY_SYMPTOMS
- CORE_SYMPTOMS should be limited (high signal only)
- Keep terms short (1–4 words)
- No explanations or reasoning

{format_instructions}

INPUT:
{symptom}

Related metadata (if any):
{metadatas}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["symptom", "metadatas"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

structured_llm = llm.with_structured_output(SymptomSummarySchema)

classifier_chain = prompt | structured_llm


def shutdown():
    subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", r".\shutdown-neo4j.ps1"],
        check=True,
    )


def restart_llm_model():
    subprocess.run(["lms", "unload", "qwen3.5-4b"])
    subprocess.run(["lms", "load", "qwen3.5-4b"])


def count_total_symptom_nodes(driver):
    records, _, _ = driver.execute_query(
        """
        MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(mr:Symptoms)
        WHERE mr.summary IS NULL OR mr.summary = "" OR mr.tags IS NULL
        RETURN count(mr) as totalNodes
        """,
        database_="neo4j",
    )

    return records[0]["totalNodes"]


def generate_symptom_summary(metadatas):
    try:
        (logging.info(f"Generating symptom summary | metadata={metadatas}"),)
        parsed_result = classifier_chain.invoke(
            {
                "symptom": metadatas.get("content", ""),
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
        core_symptoms = parsed_result.core_symptoms
        secondary_symptoms = parsed_result.secondary_symptoms
        severe_symptoms = parsed_result.severe_symptoms
        tags = parsed_result.tags

        logging.info(
            f"Summary generated successfully | summary='{summary}' | core_symptoms={core_symptoms} | secondary_symptoms={secondary_symptoms} | severe_symptoms={severe_symptoms} | tags={tags}"
        )

        return {
            "summary": summary,
            "tags": tags,
            "core_symptoms": core_symptoms,
            "secondary_symptoms": secondary_symptoms,
            "severe_symptoms": severe_symptoms,
        }

    except Exception as e:
        logging.error(f"Error generating symptom summary: {e}")
        return {
            "summary": "",
            "tags": [],
            "core_symptoms": [],
            "secondary_symptoms": [],
            "severe_symptoms": [],
        }


def batch_process_symptom_summary(driver, total_nodes):
    # Read and write 50 symptom summary at once
    BATCH_SIZE = 50

    counter = 0

    while counter < total_nodes:
        records, _, _ = driver.execute_query(
            """ 
            MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(mr:Symptoms)
            WHERE mr.summary IS NULL OR mr.summary = "" OR mr.tags IS NULL
            RETURN elementId(mr) as mr_id, mr.content as content, mr.disease_category as disease_category, o.FSN as disease_name
            ORDER BY elementId(mr)
            LIMIT $batch_size
            """,
            database="neo4j",
            batch_size=BATCH_SIZE,
        )

        symptom_ids = [r["mr_id"] for r in records]
        symptom_metadatas = [
            {
                "content": r.get("content", ""),
                "disease_category": r.get("disease_category", ""),
                "disease_name": r.get("disease_name", ""),
            }
            for r in records
        ]

        summarized_symptom = []

        for i, metadata in enumerate(symptom_metadatas):
            if i % 10 == 0:
                restart_llm_model()

            logging.info(f"Processing batch no: {counter} | item no: {i + 1}")
            print(f"Processing batch no: {counter} | item no: {i + 1}")
            summarized_symptom.append(generate_symptom_summary(metadata))

        paired_summary = [
            {
                "id": id,
                "core_symptoms": s.get("core_symptoms", []),
                "secondary_symptoms": s.get("secondary_symptoms", []),
                "severe_symptoms": s.get("severe_symptoms", []),
                "summary": s.get("summary", ""),
                "tags": s.get("tags", []),
            }
            for id, s in zip(symptom_ids, summarized_symptom)
        ]

        # Batch write
        driver.execute_query(
            """
            UNWIND $batch AS row
            MATCH (mr:Symptoms)
            WHERE elementId(mr) = row.id
            SET mr.summary = row.summary, mr.tags = row.tags, mr.core_symptoms = row.core_symptoms, mr.secondary_symptoms = row.secondary_symptoms, mr.severe_symptoms = row.severe_symptoms
            """,
            database="neo4j",
            batch=paired_summary,
        )

        counter += BATCH_SIZE
        print(f"Batch done: {counter}")
        logging.info(f"Batch done: {counter}")


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    start_time = time.perf_counter()

    total_nodes = count_total_symptom_nodes(driver)
    print(total_nodes)
    print(total_nodes)
    batch_process_symptom_summary(driver, total_nodes)

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    logging.info("Finished generating symptom summary!")
    logging.info(f"Execution time: {execution_time:.6f} seconds")
    logging.info("Shutting down PC......")
    shutdown()
