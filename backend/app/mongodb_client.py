import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[os.getenv("MONGODB_DB")]


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    dbname = get_database()
