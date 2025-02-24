from pydantic import BaseModel
import uuid
from datetime import datetime

class BaseConfig:
    from_attributes = True  # Enables ORM mode (formerly `orm_mode`)
    populate_by_name = True  # Allows aliasing of fields
    json_encoders = {
        uuid.UUID: lambda v: str(v),  # Convert UUID to string in JSON
        datetime: lambda v: v.isoformat(),  # Convert datetime to ISO format in JSON
    }

class BaseSchema(BaseModel):
    class Config(BaseConfig):
        pass