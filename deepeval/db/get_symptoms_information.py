import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URL")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

def get_symptoms_information():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        print("Quering database ...")
        records, _, _ = driver.execute_query(
            """
            MATCH (o:ObjectConcept)-[:HAS_RESOURCE]->(sym:Symptoms)
            WHERE sym.resource_title = "Malawi Standard Treatment Guidelines, sixth Edition."
            RETURN o.FSN as disease_name, collect(sym.summary) as symptoms
            LIMIT 60
            """,
            database_="neo4j",
        )

        print("Finished quering database!")
        return records
