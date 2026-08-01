from bson import ObjectId

from app.mongodb_client import get_database

db = get_database()
message_collection = db["message"]


def update_conversation_message(message_id: str, new_content: str):
    message_collection.find_one_and_update(
        {
            "_id": ObjectId(message_id),
        },
        {
            "$set": {
                "content": new_content,
            }
        },
    )
