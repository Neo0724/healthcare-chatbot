import os
from typing import List, Literal
from langchain_huggingface import HuggingFaceEmbeddings
from neo4j import GraphDatabase


URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "neoben007")

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"

embeddings_model = HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-base-v0.1")


def get_diseases_information(
    extracted_disease_name, scopes: List[Literal["Definition", "Treatment", "Symptoms"]]
):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        print("Generating disease name embedding ...")
        disease_embedding = embeddings_model.embed_query(extracted_disease_name)
        print("Finished generating disease embedding!")

        print("Quering database ...")
        records, _, _ = driver.execute_query(
            """
            OPTIONAL MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->()
            WHERE o.active = "1" AND toLower(o.FSN) = toLower($disease)

            WITH $disease_embedding as disease_embedding, o

            CALL (disease_embedding, o) {
                WITH disease_embedding, o
                WHERE o IS NULL

                MATCH (d:Description)
                WHERE d.active = "1"

                SEARCH d IN (
                    VECTOR INDEX `description_term_embed` 
                    FOR vector(disease_embedding, 768, FLOAT)
                    LIMIT 30
                ) SCORE AS score

                MATCH (vec_o:ObjectConcept)-[:HAS_DESCRIPTION]->(d)
                MATCH (vec_o)-[:HAS_RESOURCE]->()

                RETURN DISTINCT vec_o, score
                ORDER BY score DESC
                LIMIT 1
            }  

            WITH [x IN collect(DISTINCT vec_o) + collect(DISTINCT o) WHERE x IS NOT NULL] AS matched_diseases, 
                coalesce(score, 1.0) AS score

            UNWIND matched_diseases as matched_disease

            OPTIONAL MATCH (matched_disease)-[:HAS_RESOURCE]->(res)
            WHERE res.resource_title = "Malawi Standard Treatment Guidelines, sixth Edition."
            AND ANY(label IN labels(res) WHERE label IN $scopes)

            // 2. Separate and collect contents based on their node labels
            WITH matched_disease, score,
                CASE WHEN "Definition" IN labels(res) THEN "### " + res.disease_subsection + "\n" + res.content END AS def_content,
                CASE WHEN "Symptoms" IN labels(res) THEN "### " + res.disease_subsection + "\n" + res.content END AS sym_content,
                CASE WHEN "Treatment" IN labels(res) THEN "### " + res.disease_subsection + "\n" + res.content END AS treat_content

            RETURN 
                matched_disease.FSN AS disease_name, 
                score,
                collect(distinct def_content) AS definition,
                collect(distinct sym_content) AS symptom,
                collect(distinct treat_content) AS treatment

            """,
            database_="neo4j",
            disease=extracted_disease_name,
            disease_embedding=disease_embedding,
            scopes=scopes,
        )

        print("Finished quering database!")
        if not records or len(records) == 0:
            print(
                f"No information found on the given disease: {extracted_disease_name}"
            )
        else:
            print(f"Extracted disease name: **{extracted_disease_name}**")
            print(f"Queried disease name: **{records[0].data().get('disease_name')}**")
            print(f"\nQueried information\n\n{records[0]}\n")

        return records
