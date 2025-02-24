from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    """
    Construct the database connection string and SSL arguments for the development environment.
    """
    db_url = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    # SSL arguments for asyncpg
    ssl_args = {
        'ssl': 'require'  # Use 'require' for SSL connections
    }
    
    return db_url, ssl_args