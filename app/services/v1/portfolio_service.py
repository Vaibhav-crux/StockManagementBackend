from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.orders import Orders
from app.db.models.purchased_orders import PurchasedOrders
from app.db.models.ticks import Ticks
from app.db.models.users import Users
from app.schemas.portfolio import PortfolioPosition, PortfolioResponse
from fastapi import HTTPException, status
from datetime import datetime, timezone
import uuid
from app.middleware.logger import get_logger

logger = get_logger()

async def calculate_portfolio_positions(db: AsyncSession, user_id: uuid.UUID) -> PortfolioResponse:
    """
    Calculate the portfolio positions for a user based on their purchased orders.
    """
    logger.info(f"Calculating portfolio positions for user_id={user_id}")

    # Fetch all purchased orders for the given user
    result = await db.execute(select(PurchasedOrders).where(PurchasedOrders.user_id == user_id))
    purchased_orders = result.scalars().all()

    if not purchased_orders:
        logger.warning(f"No purchased orders found for user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No purchased orders found for the user",
        )

    # Group orders by ticker symbol to consolidate data
    portfolio = {}
    for order in purchased_orders:
        # Fetch the ticker symbol associated with the purchased order
        ticker_result = await db.execute(select(Ticks.ticker).where(Ticks.id == order.tick_id))
        ticker = ticker_result.scalar_one_or_none()
        if not ticker:
            logger.error(f"Ticker not found for tick_id={order.tick_id}")
            continue  # Skip this order if the ticker is not found

        symbol = ticker
        if symbol not in portfolio:
            portfolio[symbol] = {
                "total_quantity": 0,
                "total_cost": 0.0,
                "current_price": 0.0,
            }

        # Accumulate total quantity and cost for the symbol
        portfolio[symbol]["total_quantity"] += order.purchase_qty
        portfolio[symbol]["total_cost"] += order.purchase_price * order.purchase_qty

    # Calculate average price, current market price, and profit/loss (PnL) for each symbol
    positions = []
    total_pnl = 0.0
    for symbol, data in portfolio.items():
        average_price = data["total_cost"] / data["total_quantity"]

        # Fetch the latest price for the symbol from the Orders table
        latest_order_result = await db.execute(
            select(Orders.ltp)
            .join(Ticks, Ticks.id == Orders.tick_id)
            .where(Ticks.ticker == symbol)
            .order_by(Orders.timestamp.desc())
            .limit(1)
        )
        latest_order = latest_order_result.scalar_one_or_none()
        current_price = latest_order if latest_order else 0.0  # Default to 0 if no latest price found

        # Calculate Profit and Loss (PnL)
        pnl = (current_price - average_price) * data["total_quantity"]

        # Store the computed portfolio position
        positions.append(
            PortfolioPosition(
                symbol=symbol,
                quantity=data["total_quantity"],
                average_price=average_price,
                current_price=current_price,
                pnl=pnl,
                timestamp=datetime.now(timezone.utc),  # Ensure timestamp is timezone-aware
            )
        )
        total_pnl += pnl  # Sum up total PnL for all positions

    logger.info(f"Calculated portfolio positions for user_id={user_id}")
    return PortfolioResponse(
        user_id=user_id,
        positions=positions,
        total_pnl=total_pnl,
    )