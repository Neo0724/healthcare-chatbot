import os
from dotenv import load_dotenv
from typing import List
from neo4j import GraphDatabase, Record

load_dotenv()


URI = os.getenv("NEO4J_URL")
AUTH = (os.getenv("NEO4J_USERNAME"),os.getenv("NEO4J_PASSWORD"))


def get_possible_diseases(
    positive_embedding: List[float],
    negative_embedding: List[float],
) -> List[Record]:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
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
                AND s.resource_title = "Malawi Standard Treatment Guidelines, sixth Edition."
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
                WHERE s.disease_category <> "SURGERY"
                AND s.resource_title = "Malawi Standard Treatment Guidelines, sixth Edition."
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

            RETURN DISTINCT 
                post_nodes.FSN as disease_name, 
                post_nodes.id as disease_id, 
                max(post_score) as post_score, 

                collect(DISTINCT sym.summary) as symptoms

            ORDER BY post_score DESC

            LIMIT 1
            """,
            database_="neo4j",
            positive_embedding=positive_embedding,
            negative_embedding=negative_embedding,
        )

        return records
