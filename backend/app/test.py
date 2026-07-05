import logging

from app.llm.extract_symtoms import extract_medical_entities
# from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from neo4j import GraphDatabase
import os

from app.llm.extract_patient_ans import extract_patient_ans
from app.llm.get_follow_up_questions import get_follow_up_questions
from app.graph_queries.queries import get_possible_diseases, narrow_down

logging.basicConfig(
    filename="test.log",
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

    initial_input = input("Please enter your initial symptoms:\n")

    extracted_entities = extract_medical_entities(initial_input)

    positive_symptoms = extracted_entities.positive_symptoms
    negative_symptoms = extracted_entities.negative_symptoms

    positive_embedding = embeddings_model.embed_query(",".join(positive_symptoms))
    negative_embedding = embeddings_model.embed_query(",".join(negative_symptoms))

    records = get_possible_diseases(driver, positive_embedding, negative_embedding)

    initial_ids = []

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

    for i in range(5):
        logging.info(f"Question {i}\n")
        response = get_follow_up_questions(disease_summary, positive_symptoms, negative_symptoms, asked_questions)

        follow_up_question = response.question
        reason = response.reason

        asked_questions.append(response)

        logging.info(f"Question: {follow_up_question}")
        logging.info(f"Reason: {reason}")
        print(f"Question:\n{follow_up_question}\n")
        print(f"Reason:\n{reason}\n")

        patient_input = input("Answer: ")

        patient_response = extract_patient_ans(follow_up_question, patient_input)

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