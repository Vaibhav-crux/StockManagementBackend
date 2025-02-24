from pydantic import BaseModel
import uuid
from app.schemas.base import BaseSchema

class PurchasedOrderCreate(BaseModel):
    tick_id: uuid.UUID
    purchase_price: float
    purchase_qty: int

class PurchasedOrderResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    tick_id: uuid.UUID
    purchase_price: float
    purchase_qty: int
    timestamp: str

class PurchasedOrdersResponse(BaseSchema):
    orders: list[PurchasedOrderResponse]
    total: int
    skip: int
    limit: int
