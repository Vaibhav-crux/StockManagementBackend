import os
import uvicorn
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config.db_connection import get_db_connection
from app.main import app
from app.db.session import create_tables

async def check_db_connection():
    """
    Check if the database connection is valid using the connection string and SSL args.
    """
    try:
        db_connection_string, ssl_args = get_db_connection()
        
        engine = create_async_engine(db_connection_string, connect_args=ssl_args)
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        print("Database connection established successfully.")
        return True
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False

async def startup_event():
    """
    Perform startup checks and create tables if they don't exist.
    """
    # Check database connection
    if not await check_db_connection():
        raise RuntimeError("Server startup halted due to database connection failure.")
    
    # Create tables if they don't exist
    try:
        await create_tables()
        print("Database tables checked/created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise RuntimeError("Server startup halted due to table creation failure.")

# Startup event to the FastAPI app
@app.on_event("startup")
async def startup():
    await startup_event()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  
    uvicorn.run("app.server:app", host="0.0.0.0", port=port, reload=True)