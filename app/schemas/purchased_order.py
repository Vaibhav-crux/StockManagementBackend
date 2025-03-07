from pydantic import BaseModel, Field
import uuid
from app.schemas.base import BaseSchema

class PurchasedOrderCreate(BaseModel):
    tick_id: uuid.UUID
    purchase_price: float
    purchase_qty: int

class PurchasedOrderResponse(BaseSchema):
    id: str = Field(...)
    user_id: str = Field(...)
    tick_id: str = Field(...)
    purchase_price: float
    purchase_qty: int
    timestamp: str
    ticker: str = Field(None, description="Ticker name associated with the tick_id")

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            user_id=str(obj.user_id),
            tick_id=str(obj.tick_id),
            purchase_price=obj.purchase_price,
            purchase_qty=obj.purchase_qty,
            timestamp=obj.timestamp.isoformat(),
            ticker=getattr(obj, 'ticker', None)
        )

class PurchasedOrdersResponse(BaseSchema):
    orders: list[PurchasedOrderResponse]
    total: int
    skip: int
    limit: int

# Schema for the simplified /place-order response
class PlaceOrderResponse(BaseModel):
    id: str = Field(...)
    message: str = Field(..., description="Confirmation message")