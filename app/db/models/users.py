from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.utils.base_model import BaseModel

class Users(BaseModel):
    __tablename__ = 'users'

    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    def __repr__(self):
        return f"<Users(email='{self.email}', created_at='{self.created_at}')>"