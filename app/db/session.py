from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.db_connection import get_db_connection
from app.utils.base_model import Base

# Get the database connection string and SSL arguments
db_connection_string, ssl_args = get_db_connection()

# Create the async engine with the connection string and SSL arguments
engine = create_async_engine(db_connection_string, connect_args=ssl_args)

# Create a configured "AsyncSessionLocal" class
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Create all tables in the database
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dependency to get the database session
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()