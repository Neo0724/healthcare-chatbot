import os

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URL")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

driver: Driver = None


def get_neo4j_driver():
    global driver
    if not driver:
        driver = GraphDatabase.driver(
            URI,
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
        )

    return driver
