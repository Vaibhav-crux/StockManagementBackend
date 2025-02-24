from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    return os.getenv('PROD_DB_CONNECTION')