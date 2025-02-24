import os
import uvicorn
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config.db_connection import get_db_connection
from app.main import app

async def check_db_connection():
    """
    Check if the database connection is valid using the connection string and SSL args.
    """
    try:
        db_connection_string, ssl_args = get_db_connection()
        
        # Use an asynchronous SQLAlchemy engine to validate the connection
        engine = create_async_engine(db_connection_string, connect_args=ssl_args)
        async with engine.connect() as connection:
            # Use SQLAlchemy's text() function to wrap the raw SQL query
            await connection.execute(text("SELECT 1"))  # Simple query to validate the connection
        print("Database connection established successfully.")
        return True
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False

# Perform DB check before starting the app
async def startup_event():
    if not await check_db_connection():
        raise RuntimeError("Server startup halted due to database connection failure.")

# Attach the startup event to the FastAPI app
@app.on_event("startup")
async def startup():
    await startup_event()

# Run Uvicorn only when executed directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  
    uvicorn.run("app.server:app", host="0.0.0.0", port=port, reload=True)