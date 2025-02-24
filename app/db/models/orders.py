from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey, event, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.utils.base_model import BaseModel
from sqlalchemy.sql import func
from .ticks import Ticks

class Orders(BaseModel):
    __tablename__ = 'orders'

    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    ltp = Column(Float, nullable=False)
    buyprice = Column(Float, nullable=False)
    buyqty = Column(Integer, nullable=False)
    sellprice = Column(Float, nullable=False)
    sellqty = Column(Integer, nullable=False)
    ltq = Column(Integer, nullable=False)
    openinterest = Column(Integer, nullable=False)

    # Foreign Key to link with Ticks
    tick_id = Column(UUID(as_uuid=True), ForeignKey('ticks.id'), nullable=False)

    # Relationship to access the related tick
    tick = relationship("Ticks", back_populates="orders", foreign_keys=[tick_id])

    # Composite index for faster lookups
    __table_args__ = (
        Index('ix_orders_tick_id_timestamp', 'tick_id', timestamp.desc()),
    )

    def __repr__(self):
        return f"<Orders(tick_id={self.tick_id}, timestamp='{self.timestamp}', ltp={self.ltp}, sellprice={self.sellprice}, sellqty={self.sellqty}, ltq={self.ltq}, openinterest={self.openinterest})>"

# Event listener to update the latest_order_id in Ticks when a new order is added
@event.listens_for(Orders, 'after_insert')
def update_latest_order_id(mapper, connection, target):
    connection.execute(
        Ticks.__table__.update().where(Ticks.id == target.tick_id).values(latest_order_id=target.id)
    )