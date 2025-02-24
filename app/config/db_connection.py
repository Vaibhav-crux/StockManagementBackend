from dotenv import load_dotenv
import os
from .production_db import get_db_connection as get_prod_db
from .development_db import get_db_connection as get_dev_db

# Load environment variables
load_dotenv()

def get_db_connection():
    # Determine which environment we're in
    db_env = os.getenv('DB_ENV', 'development').lower()
    
    if db_env == 'production':
        return get_prod_db()
    elif db_env == 'development':
        return get_dev_db()
    else:
        raise ValueError(f"Unknown database environment: {db_env}")