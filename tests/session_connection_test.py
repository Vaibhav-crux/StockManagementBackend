from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.db_connection import get_db_connection
from app.utils.base_model import Base
from app.db.models.ticks import Ticks
from app.db.models.orders import Orders
from app.db.models.users import Users
from app.db.models.purchased_orders import PurchasedOrders

# Get the database connection string and SSL arguments
db_connection_string, ssl_args = get_db_connection()

# Create the engine with the connection string and SSL arguments
engine = create_engine(db_connection_string, connect_args=ssl_args)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()