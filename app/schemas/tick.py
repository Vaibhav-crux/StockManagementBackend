from pydantic import validator, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
from app.schemas.order import OrderResponse
from app.schemas.base import BaseSchema

class TickResponse(BaseSchema):
    """Response schema for a single ticker."""
    id: uuid.UUID
    ticker: str

class OrderDetailsResponse(BaseSchema):
    """Response schema containing order details for a specific ticker."""
    ticker: str
    orders: List[OrderResponse]
    total: int
    skip: int
    limit: int
    interval: Optional[int] = Field(default=None, description="Time interval in minutes for filtering orders")

class TickerWithDates(BaseSchema):
    """Schema for ticker details along with historical data."""
    id: uuid.UUID
    ticker: str
    dates: List[str]
    sellqty: Optional[int] = Field(default=None, description="Total quantity of shares sold")
    sellprice: Optional[float] = Field(default=None, description="Selling price of the shares")
    ltp: Optional[float] = Field(default=None, description="Last traded price")
    ltq: Optional[int] = Field(default=None, description="Last traded quantity")
    latest_timestamp: Optional[str] = Field(default=None, description="Timestamp of the most recent trade")

    @validator('id', 'latest_timestamp', pre=True)
    def convert_uuid_and_datetime(cls, value):
        """Ensure UUIDs are converted to strings and datetime objects are formatted as ISO strings."""
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

class TickerSearchResponse(BaseSchema):
    """Response schema for paginated ticker search results."""
    tickers_with_dates: List[TickerWithDates]
    total: int
    skip: int
    limit: int

class OHLCResponse(BaseSchema):
    """Schema representing Open, High, Low, and Close (OHLC) price data for a ticker."""
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
