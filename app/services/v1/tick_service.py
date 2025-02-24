from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models.ticks import Ticks
from app.db.models.orders import Orders
from typing import List, Optional, Tuple
import uuid
from datetime import datetime, date, timedelta
from app.schemas.tick import TickerWithDates, OrderResponse
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from app.middleware.websocket_manager import websocket_manager
from app.middleware.logger import get_logger
from app.schemas.tick import OHLCResponse

load_dotenv()

logger = get_logger()

async def get_tickers(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Tuple[List[TickerWithDates], int, int, int]:
    logger.info(f"Fetching tickers with skip={skip}, limit={limit}, search={search}, start_date={start_date}, end_date={end_date}")
    if start_date and end_date and end_date < start_date:
        logger.error("end_date cannot be less than start_date")
        raise HTTPException(status_code=400, detail="end_date cannot be less than start_date")

    # Subquery to get the latest order per tick with necessary fields
    subquery = (
        select(
            Orders.tick_id,
            Orders.timestamp,
            Orders.sellqty,
            Orders.sellprice,
            Orders.ltp,
            Orders.ltq,
            func.row_number().over(
                partition_by=Orders.tick_id,
                order_by=Orders.timestamp.desc()
            ).label('rn')
        )
        .where(
            (Orders.timestamp >= start_date if start_date else True) &
            (Orders.timestamp <= end_date if end_date else True)
        )
        .subquery()
    )

    # Main query to join Ticks with the latest orders
    query = (
        select(
            Ticks.id,
            Ticks.ticker,
            subquery.c.timestamp,
            subquery.c.sellqty,
            subquery.c.sellprice,
            subquery.c.ltp,
            subquery.c.ltq
        )
        .join(subquery, Ticks.id == subquery.c.tick_id)
        .where(subquery.c.rn == 1)
        .order_by(Ticks.ticker)
        .offset(skip)
        .limit(limit)
    )

    if search:
        query = query.where(Ticks.ticker.ilike(f"%{search}%"))

    result = await db.execute(query)
    ticks = result.all()

    # Build results without additional queries
    results = []
    for tick_id, ticker, timestamp, sellqty, sellprice, ltp, ltq in ticks:
        latest_date = timestamp.strftime("%d-%m-%Y") if timestamp else None
        ticker_with_dates = TickerWithDates(
            id=str(tick_id),
            ticker=ticker,
            dates=[latest_date] if latest_date else [],
            interval=None,
            sellqty=sellqty,
            sellprice=sellprice,
            ltp=ltp,
            ltq=ltq,
            latest_timestamp=timestamp.isoformat() if timestamp else None
        )
        results.append(ticker_with_dates)

    total = await get_total_tickers_count(db, search, start_date, end_date)
    logger.info(f"Total tickers count: {total}")
    return results, total, skip, limit

async def get_total_tickers_count(
    db: AsyncSession,
    search: str = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> int:
    """
    Get the total count of distinct tickers, optionally filtered by search and date range.
    """
    # Subquery to get distinct tickers
    subquery = (
        select(Ticks.ticker)
        .distinct()
        .subquery()
    )

    # Base query to count distinct tickers
    query = select(func.count()).select_from(subquery)

    # Apply search filter
    if search:
        query = query.where(subquery.c.ticker.ilike(f"%{search}%"))

    # Apply date filters
    if start_date or end_date:
        # Join the Orders table with the Ticks table
        query = query.join(Ticks, subquery.c.ticker == Ticks.ticker)
        query = query.join(Orders, Ticks.id == Orders.tick_id)
        if start_date:
            query = query.where(Orders.timestamp >= start_date)
        if end_date:
            query = query.where(Orders.timestamp <= end_date)

    # Execute the query and return the count
    result = await db.execute(query)
    count = result.scalar()
    logger.debug(f"Computed total tickers count: {count}")
    return count

async def get_orders_by_tick_id(
    db: AsyncSession,
    tick_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    interval: Optional[int] = None
) -> Optional[dict]:
    logger.info(f"Fetching orders for tick_id={tick_id}, skip={skip}, limit={limit}, interval={interval}")
    tick = await db.execute(select(Ticks).where(Ticks.id == tick_id))
    tick = tick.scalar_one_or_none()
    if not tick:
        logger.warning(f"No ticker found for tick_id={tick_id}")
        return None

    orders_query = select(Orders).where(Orders.tick_id == tick_id)
    if interval is not None:
        if interval < 0:
            logger.error("Interval must be a positive number")
            raise HTTPException(status_code=400, detail="Interval must be a positive number")
        current_time = datetime.now()
        time_threshold = current_time - timedelta(minutes=interval)
        orders_query = orders_query.where(Orders.timestamp >= time_threshold)

    orders_query = orders_query.order_by(Orders.timestamp.desc())
    total_orders = await db.execute(select(func.count()).select_from(orders_query))
    total_orders = total_orders.scalar()
    orders = await db.execute(orders_query.offset(skip).limit(limit))
    orders = orders.scalars().all()

    if not orders and total_orders == 0:
        logger.info(f"No orders found for tick_id={tick_id}")
        return None

    orders_list = [OrderResponse.from_orm(order) for order in orders]
    logger.info(f"Retrieved {len(orders_list)} orders for tick_id={tick_id}")
    return {
        "ticker": tick.ticker,
        "orders": orders_list,
        "total": total_orders,
        "skip": skip,
        "limit": limit,
        "interval": interval
    }

async def update_tickers(db: AsyncSession):
    logger.info("Updating tickers via WebSocket")
    tickers, total, skip, limit = await get_tickers(db)
    await websocket_manager.broadcast({
        "tickers_with_dates": tickers,
        "total": total,
        "skip": skip,
        "limit": limit
    })
    logger.info("Tickers updated and broadcasted via WebSocket")

async def get_ohlc_data(
    db: AsyncSession,
    ticker: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[OHLCResponse]:
    """
    Aggregate second-level tick data into daily OHLC (Open-High-Low-Close) format.
    """
    logger.info(f"Fetching OHLC data for ticker={ticker}, start_date={start_date}, end_date={end_date}")

    # Subquery for daily low/high
    high_low_subquery = (
        select(
            func.date(Orders.timestamp).label("date"),
            func.min(Orders.ltp).label("low"),
            func.max(Orders.ltp).label("high")
        )
        .join(Ticks, Ticks.id == Orders.tick_id)
        .where(Ticks.ticker == ticker)
        .group_by(func.date(Orders.timestamp))
        .subquery()
    )

    # Subquery for daily open price (first price of the day)
    open_subquery = (
        select(
            func.date(Orders.timestamp).label("date"),
            Orders.ltp.label("open")
        )
        .join(Ticks, Ticks.id == Orders.tick_id)
        .where(Ticks.ticker == ticker)
        .distinct(func.date(Orders.timestamp))
        .order_by(func.date(Orders.timestamp), Orders.timestamp.asc())
        .subquery()
    )

    # Subquery for daily close price (last price of the day)
    close_subquery = (
        select(
            func.date(Orders.timestamp).label("date"),
            Orders.ltp.label("close")
        )
        .join(Ticks, Ticks.id == Orders.tick_id)
        .where(Ticks.ticker == ticker)
        .distinct(func.date(Orders.timestamp))
        .order_by(func.date(Orders.timestamp), Orders.timestamp.desc())
        .subquery()
    )

    # Main query joining all subqueries
    query = (
        select(
            high_low_subquery.c.date,
            open_subquery.c.open,
            high_low_subquery.c.high,
            high_low_subquery.c.low,
            close_subquery.c.close
        )
        .join(open_subquery, high_low_subquery.c.date == open_subquery.c.date)
        .join(close_subquery, high_low_subquery.c.date == close_subquery.c.date)
    )

    if start_date:
        query = query.where(high_low_subquery.c.date >= start_date)
    if end_date:
        query = query.where(high_low_subquery.c.date <= end_date)

    result = await db.execute(query)
    ohlc_data = result.all()

    if not ohlc_data:
        logger.warning(f"No OHLC data found for ticker={ticker}")
        raise HTTPException(status_code=404, detail="No OHLC data found for the given ticker and date range")

    # Convert results to OHLCResponse objects
    results = [
        OHLCResponse(
            ticker=ticker,
            date=row.date,
            open=row.open,
            high=row.high,
            low=row.low,
            close=row.close
        )
        for row in ohlc_data
    ]

    logger.info(f"Retrieved {len(results)} OHLC records for ticker={ticker}")
    return results