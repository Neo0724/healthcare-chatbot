from typing import List

from neo4j import Driver, Record


def get_possible_diseases(
    driver: Driver, positive_embedding: List[float], negative_embedding: List[float]
) -> List[Record]:
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

        RETURN DISTINCT 
            post_nodes.FSN as disease_name, 
            post_nodes.id as disease_id, 
            max(post_score) as post_score, 
            collect({
                summary: sym.summary, 
                resource_title: sym.resource_title,
                resource_author: sym.resource_author,
                resource_published_year: sym.resource_published_year,
                resource_url: sym.resource_url
            }) as symptom_node

        ORDER BY post_score DESC

        LIMIT 5
        """,
        database_="neo4j",
        positive_embedding=positive_embedding,
        negative_embedding=negative_embedding,
    )

    return records


def narrow_down(
    driver: Driver,
    positive_embedding: List[float],
    negative_embedding: List[float],
    initial_ids: List[str],
) -> List[Record]:
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

        // WHERE post_nodes.id in $initial_ids

        RETURN DISTINCT 
            post_nodes.FSN as disease_name, 
            post_nodes.id as disease_id, 
            max(post_score) as post_score, 

            collect({
                summary: sym.content, 
                resource_title: sym.resource_title,
                resource_author: sym.resource_author,
                resource_published_year: sym.resource_published_year,
                resource_url: sym.resource_url
            }) as symptom_node

        ORDER BY post_score DESC

        LIMIT 5
        """,
        database_="neo4j",
        positive_embedding=positive_embedding,
        negative_embedding=negative_embedding,
        initial_ids=initial_ids,
    )

    return records


def get_diseases_information(
    driver: Driver, diseases: List[str], diseases_embedding: List[float]
):
    records, _, _ = driver.execute_query(
        """
        UNWIND range(0, size($diseases)-1) AS i
        WITH $diseases[i] AS disease, $diseases_embedding[i] AS disease_embedding

        OPTIONAL MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->()
        WHERE o.active = "1" AND toLower(o.FSN) = toLower(disease)

        WITH disease, disease_embedding, o

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

        OPTIONAL MATCH (matched_disease)-[:HAS_RESOURCE]->(def:Definition)
        OPTIONAL MATCH (matched_disease)-[:HAS_RESOURCE]->(sym:Symptoms)
        OPTIONAL MATCH (matched_disease)-[:HAS_RESOURCE]->(treat:Treatment)

        RETURN matched_disease.FSN AS disease_name, 
            score,
            collect({
              content: def.content,
              resource_title: def.resource_title,    
              resource_author: def.resource_author,    
              resource_published_year: def.resource_published_year,    
              resource_url: def.resource_url    
            }) AS definition_node,

            collect({
              content: sym.content,
              resource_title: sym.resource_title,    
              resource_author: sym.resource_author,    
              resource_published_year: sym.resource_published_year,    
              resource_url: sym.resource_url    
            }) AS symptom_node,

            collect({
              content: treat.content,
              resource_title: treat.resource_title,    
              resource_author: treat.resource_author,    
              resource_published_year: treat.resource_published_year,    
              resource_url: treat.resource_url    
            }) AS treatment_node        
        """,
        database_="neo4j",
        diseases=diseases,
        diseases_embedding=diseases_embedding,
    )

    return records
