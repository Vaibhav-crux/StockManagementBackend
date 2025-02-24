from sqlalchemy import Column, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.utils.base_model import BaseModel

class Ticks(BaseModel):
    __tablename__ = 'ticks'

    ticker = Column(String, nullable=False, index=True)
    latest_order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=True)
    __table_args__ = (UniqueConstraint('ticker', name='uq_ticks_ticker'),)  # Ensure uniqueness

    # Relationship to orders (one tick can have multiple orders)
    orders = relationship("Orders", back_populates="tick", cascade="all, delete-orphan", foreign_keys="Orders.tick_id")

    # Relationship to the latest order
    latest_order = relationship("Orders", foreign_keys=[latest_order_id], post_update=True)

    def __repr__(self):
        return f"<Ticks(ticker='{self.ticker}')>"
