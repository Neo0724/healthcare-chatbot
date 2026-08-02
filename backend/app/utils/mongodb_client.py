import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = None


def get_database():

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    global client
    if not client:
        client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[os.getenv("MONGODB_DB")]