import json
import logging
import os
import subprocess
import time
from typing import Literal

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import MarkdownHeaderTextSplitter
from neo4j import GraphDatabase
from pydantic import BaseModel, Field

logging.basicConfig(
    filename="logs/relationship-malawi-stg.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

load_dotenv()

URI = os.getenv("NEO4J_URL")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
MARKDOWN_FILE_NAME = "markdowns/malawi-stg-cleaned.md"

# Create embedding model
embeddings_model = HuggingFaceEmbeddings(model_name="SalmanFaroz/DisEmbed-v1")


# 1. Define the Pydantic Schema
class NodeTitleSchema(BaseModel):
    node_title: Literal["Symptoms", "Treatment", "Definition"] = Field(
        description="The category of the medical text snippet"
    )


# 2. Initialize the Parser
parser = PydanticOutputParser(pydantic_object=NodeTitleSchema)

# 3. Setup LLM
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="qwen3.5-4b",
    temperature=0,
)

# 4. Create Prompt Template using format_instructions
prompt_template = """
You are a medical classifier. 
Classify the text into one of these three categories:
- Definition: Explains what the disease is, its origin, or its biological nature.
- Symptoms: Lists physical signs, clinical criteria, or what the patient experiences.
- Treatment: Lists medications, procedures, or management steps.

{format_instructions}

Text to analyze:
{text}

Headers related to the text
{header}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["text", "header"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

structured_llm = llm.with_structured_output(NodeTitleSchema)

classifier_chain = prompt | structured_llm


def restart_llm_model():
    subprocess.run(["lms", "unload", "qwen3.5-4b"])
    subprocess.run(["lms", "load", "qwen3.5-4b"])


def shutdown():
    subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", r".\shutdown-neo4j.ps1"],
        check=True,
    )


def classify_chunks(chunk):

    result: NodeTitleSchema = "Symptoms"
    try:
        (
            logging.info(
                f"Classifying chunk | content_length='{len(chunk.page_content)}' | metadata={chunk.metadata}"
            ),
        )
        parsed_result = classifier_chain.invoke(
            {
                "text": chunk.page_content,
                "header": json.dumps(chunk.metadata, ensure_ascii=False),
            }
        )

        result = parsed_result.node_title
        logging.info(f"Classification successful | result='{result}'")
        return result

    except Exception as e:
        logging.info(f"Classification failed | error=f{str(e)}")
        return result


def match_disease_from_db(driver, disease_name):
    disease_concept_id = None
    disease_concept_name = ""

    logging.info(f"Starting disease match | disease_name='{disease_name}'")

    try:
        records, _, _ = driver.execute_query(
            """
            MATCH (o: ObjectConcept)-[:HAS_DESCRIPTION]-(d:Description) 
            WHERE toLower(d.term) = toLower($disease_name)
            RETURN o.id, o.FSN
            LIMIT 1;
            """,
            database_="neo4j",
            disease_name=disease_name,
        )

        logging.info(f"Exact match results count = {len(records)}")

        if len(records) == 1:
            disease_concept_id = records[0]["o.id"]
            disease_concept_name = records[0]["o.FSN"]
            logging.info(
                f"Exact match found | concept_id={disease_concept_id} | concept_term='{disease_concept_name}'"
            )

        else:
            logging.info("No exact match found, switching to embedding search")

            embedding = embeddings_model.embed_query(disease_name)
            records, _, _ = driver.execute_query(
                """
                MATCH (d:Description)
                SEARCH d IN (
                    VECTOR INDEX `description_term_embed`
                    FOR vector($embedding, 768, FLOAT NOT NULL)
                    LIMIT 1
                ) SCORE AS score
                MATCH (o:ObjectConcept)-[:HAS_DESCRIPTION]->(des: Description {id: d.id})
                RETURN o.id, o.FSN, score;
                """,
                database="neo4j",
                embedding=embedding,
            )

            logging.info(f"Vector search returned {len(records)} candidates")

            if len(records) == 0:
                logging.warning(
                    "Vector search return empty result | Disease Name='{disease_name}'"
                )

            else:
                top_score_concept = records[0]
                disease_concept_id = top_score_concept["o.id"]
                disease_concept_name = top_score_concept["o.FSN"]
                score = top_score_concept["score"]

                logging.info(
                    f"Best semantic match selected | concept_id={disease_concept_id} | concept_term='{disease_concept_name}' | score={score}"
                )

        logging.info(
            f"Final result concept_id={disease_concept_id} | concept_term='{disease_concept_name}'"
        )
        return disease_concept_id

    except Exception as e:
        logging.error(f"Error when matching disease from database | Error={e}")
        return None


def create_relationship(driver, disease_concept_id, chunk, node_title):
    logging.info(
        f"Creating relationship | concept_id={disease_concept_id} | "
        f"node_title='{node_title}' | content_length={len(chunk.page_content)} | "
        f"metadata={chunk.metadata}"
    )

    try:
        _, _, _ = driver.execute_query(
            """
            MATCH (o:ObjectConcept)
            WHERE o.id = $disease_concept_id

            CALL apoc.create.node(
                [$node_title],
                {
                    content: $content,
                    disease_category: $disease_category,
                    disease_name: $disease_name,
                    disease_subsection: $disease_subsection,
                    resource_title: $resource_title,
                    resource_author: $resource_author,
                    resource_published_year: $resource_published_year,
                    resource_url: $resource_url
                }
            ) YIELD node as med_resource

            WITH o, med_resource

            CALL apoc.create.relationship(o, "HAS_RESOURCE", {}, med_resource) YIELD rel

            RETURN rel;
            """,
            database="neo4j",
            disease_concept_id=disease_concept_id,
            content=chunk.page_content,
            disease_category=chunk.metadata.get("Disease Category", ""),
            disease_name=chunk.metadata.get("Disease Name", ""),
            disease_subsection=chunk.metadata.get("Subsection", ""),
            resource_title=chunk.metadata.get("resource_title", ""),
            resource_author=chunk.metadata.get("resource_author", ""),
            resource_published_year=chunk.metadata.get("resource_published_year", ""),
            resource_url=chunk.metadata.get("resource_url", ""),
            node_title=node_title,
        )

        logging.info(
            f"Relationship created successfully | concept_id={disease_concept_id} | node_title='{node_title}'"
        )

    except Exception as e:
        logging.error(f"Error when creating relationship | Error={e}")


def run_pipeline():

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        start_time = time.perf_counter()

        logging.info(
            "Starting to create relationship between medical chunk and SNOMED-CT concept node"
        )

        # 1. Load and Split
        try:
            with open(MARKDOWN_FILE_NAME, "r", encoding="utf-8") as f:
                markdown_file = f.read()

            headers_to_split_on = [
                ("#", "Disease Category"),
                ("##", "Disease Name"),
                ("###", "Subsection"),
            ]

            header_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=headers_to_split_on
            )

            split_docs = header_splitter.split_text(markdown_file)

            for i, doc in enumerate(split_docs):
                logging.info(f"Processing chunk - {i + 1}:")
                if i % 10 == 0:
                    restart_llm_model()

                if (
                    "Subsection" in doc.metadata
                    and doc.metadata["Subsection"] == "References"
                ):
                    continue

                disease_concept_id = match_disease_from_db(
                    driver, doc.metadata.get("Disease Name", "")
                )

                if disease_concept_id:
                    node_title = classify_chunks(doc)

                    doc.metadata["resource_title"] = (
                        "Malawi Standard Treatment Guidelines, sixth Edition."
                    )
                    doc.metadata["resource_author"] = "Malawi Ministry of Health"
                    doc.metadata["resource_published_year"] = 2023
                    doc.metadata["resource_url"] = (
                        "https://digrep.mchs.mw/items/a78a9b82-667e-4e50-8005-a11f3308d676"
                    )

                    create_relationship(driver, disease_concept_id, doc, node_title)

                else:
                    logging.warning(
                        f"Disease concept id is not found | Disease name={doc.metadata.get('Disease Name', '')}"
                    )

            end_time = time.perf_counter()

            execution_time = end_time - start_time
            logging.info(
                "Finished creating relationship chunk of Malawi Standard Treatment Guidelines, sixth Edition.!"
            )
            logging.info(f"Execution time: {execution_time:.6f} seconds")
            # logging.info("Shutting down Neo4j instance and PC......")
            # shutdown()

        except FileNotFoundError as e:
            print(f"File not found. {e}")


if __name__ == "__main__":
    run_pipeline()
