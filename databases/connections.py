from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

def get_collection(database_name="stock_db", collection_name="daily_transactions"):
    db = client[database_name]
    collection = db[collection_name]
    return collection

