from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID  # Import UUID for PostgreSQL
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import uuid  # Python's built-in UUID module

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True  # This makes the class abstract, so it won't create a table for this class

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)  # Use UUID as the primary key
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())