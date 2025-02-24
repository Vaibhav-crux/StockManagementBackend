from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
from app.schemas.base import BaseSchema

class PortfolioPosition(BaseSchema):
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    pnl: float = Field(description="Profit and Loss")
    timestamp: datetime

class PortfolioResponse(BaseSchema):
    user_id: uuid.UUID
    positions: List[PortfolioPosition]
    total_pnl: float