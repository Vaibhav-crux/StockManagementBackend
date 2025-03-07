from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.utils.base_model import BaseModel
from sqlalchemy.sql import func
from sqlalchemy import desc

class PurchasedOrders(BaseModel):
    __tablename__ = 'purchased_orders'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    tick_id = Column(UUID(as_uuid=True), ForeignKey('ticks.id'), nullable=False, index=True)
    purchase_price = Column(Float, nullable=False)
    purchase_qty = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)

    # Relationships
    user = relationship("Users", back_populates="orders")
    tick = relationship("Ticks", back_populates="purchased_orders")

    # Composite index for user_id and timestamp (descending)
    __table_args__ = (
        Index('idx_purchased_orders_user_id_timestamp_desc', 'user_id', desc('timestamp')),
    )

    def __repr__(self):
        return f"<PurchasedOrders(user_id={self.user_id}, tick_id={self.tick_id}, purchase_price={self.purchase_price}, purchase_qty={self.purchase_qty}, timestamp='{self.timestamp}')>"

from app.db.models.users import Users
from app.db.models.ticks import Ticks

Users.orders = relationship("PurchasedOrders", back_populates="user", cascade="all, delete-orphan")
Ticks.purchased_orders = relationship("PurchasedOrders", back_populates="tick", cascade="all, delete-orphan")