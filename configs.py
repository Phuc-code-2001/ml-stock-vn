import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

INTRA_DATA_FOLDER = './data'
UPDATE_DATA_PASSWORD = os.getenv("UPDATE_DATA_PASSWORD")