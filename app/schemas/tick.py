from pydantic import validator, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
from app.schemas.order import OrderResponse
from app.schemas.base import BaseSchema  # Import BaseSchema from base.py

# Schema for Tick response
class TickResponse(BaseSchema):
    id: uuid.UUID
    ticker: str

# Schema for Order details response
class OrderDetailsResponse(BaseSchema):
    ticker: str
    orders: List[OrderResponse]
    total: int
    skip: int
    limit: int
    interval: Optional[int] = Field(default=None, description="Optional interval for the response")

# Schema for Ticker with dates
class TickerWithDates(BaseSchema):
    id: uuid.UUID
    ticker: str
    dates: List[str]
    sellqty: Optional[int] = Field(default=None, description="Quantity of shares sold")
    sellprice: Optional[float] = Field(default=None, description="Price at which shares were sold")
    ltp: Optional[float] = Field(default=None, description="Last traded price")
    ltq: Optional[int] = Field(default=None, description="Last traded quantity")
    latest_timestamp: Optional[str] = Field(default=None, description="Timestamp of the latest trade")

    # Validator to convert UUID and datetime to strings
    @validator('id', 'latest_timestamp', pre=True)
    def convert_uuid_and_datetime(cls, value):
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

# Schema for Ticker search response
class TickerSearchResponse(BaseSchema):
    tickers_with_dates: List[TickerWithDates]
    total: int
    skip: int
    limit: int

# Schema for OHLC (Open, High, Low, Close) response
class OHLCResponse(BaseSchema):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float