from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from app.schemas.base import BaseSchema

class OrderResponse(BaseSchema):
    id: uuid.UUID
    ltp: float
    sellprice: float
    sellqty: int
    ltq: int
    openinterest: int
    tick_id: uuid.UUID
    buyprice: float
    buyqty: int
    timestamp: str = Field(description="Original timestamp")
    date: str = Field(description="Extracted date (dd/mm/yyyy)")
    time: str = Field(description="Extracted time (hh:mm:ss)")

    @classmethod
    def from_orm(cls, obj):
        formatted_date = obj.timestamp.strftime("%d/%m/%Y") if obj.timestamp else None
        formatted_time = obj.timestamp.strftime("%H:%M:%S") if obj.timestamp else None
        return cls(
            id=obj.id,
            ltp=obj.ltp,
            sellprice=obj.sellprice,
            sellqty=obj.sellqty,
            ltq=obj.ltq,
            openinterest=obj.openinterest,
            tick_id=obj.tick_id,
            buyprice=obj.buyprice,
            buyqty=obj.buyqty,
            timestamp=obj.timestamp.isoformat() if obj.timestamp else None,
            date=formatted_date,
            time=formatted_time
        )