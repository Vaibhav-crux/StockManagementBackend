from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
from app.schemas.base import BaseSchema

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseSchema):
    id: uuid.UUID
    email: EmailStr

class Token(BaseSchema):
    access_token: str
    token_type: str = Field(default="bearer", description="Type of the token")