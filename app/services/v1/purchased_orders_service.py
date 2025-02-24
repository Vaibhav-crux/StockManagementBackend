from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models.orders import Orders
from app.db.models.purchased_orders import PurchasedOrders
from app.db.models.ticks import Ticks
from app.db.models.users import Users
from app.schemas.purchased_order import PurchasedOrderCreate, PurchasedOrderResponse
from fastapi import HTTPException, status
from datetime import datetime
import uuid
from app.middleware.jwt import JWTHandler
from app.middleware.logger import get_logger
from app.config.redis_client_connection import redis_client
import json

logger = get_logger()

async def get_current_user(token: str, db: AsyncSession):
    logger.info("Validating user token")
    payload = JWTHandler.decode_token(token)
    user_id = payload.get("sub")
    
    # Corrected select statement with proper closing parenthesis
    result = await db.execute(select(Users).where(Users.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        logger.warning(f"No user found for user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"User authenticated: {user.email}")
    return user

async def place_order(db: AsyncSession, order: PurchasedOrderCreate, token: str) -> PurchasedOrderResponse:
    logger.info(f"Placing order for tick_id={order.tick_id}, purchase_price={order.purchase_price}")
    user = await get_current_user(token, db)
    
    result = await db.execute(select(Ticks).where(Ticks.id == order.tick_id))
    tick = result.scalar_one_or_none()
    if not tick:
        logger.error(f"Ticker not found for tick_id={order.tick_id}")
        raise HTTPException(status_code=404, detail="Ticker not found")

    new_order = Orders(
        tick_id=order.tick_id,
        ltp=order.purchase_price,
        buyprice=order.purchase_price,
        buyqty=order.purchase_qty,
        sellprice=0.0,
        sellqty=0,
        ltq=0,
        openinterest=0
    )
    db.add(new_order)
    await db.flush()  # Flush to get the ID of new_order without committing yet
    
    tick.latest_order_id = new_order.id
    
    db_order = PurchasedOrders(
        user_id=user.id,
        tick_id=order.tick_id,
        purchase_price=order.purchase_price,
        purchase_qty=order.purchase_qty
    )
    db.add(db_order)
    await db.commit()  # Single commit for all operations
    
    await db.refresh(new_order)
    await db.refresh(db_order)
    logger.info(f"New order created with id={new_order.id}, Purchased order recorded with id={db_order.id}")

    # Invalidate the cache for this user's purchased orders
    cache_key_pattern = f"purchased_orders:{user.id}:*"
    cache_keys = redis_client.keys(cache_key_pattern)
    if cache_keys:
        redis_client.delete(*cache_keys)
        logger.info(f"Cache invalidated for keys: {cache_keys}")

    return PurchasedOrderResponse(
        id=db_order.id,
        user_id=db_order.user_id,
        tick_id=db_order.tick_id,
        purchase_price=db_order.purchase_price,
        purchase_qty=db_order.purchase_qty,
        timestamp=db_order.timestamp.isoformat()
    )

async def get_purchased_orders_by_user(db: AsyncSession, user: Users, skip: int = 0, limit: int = 100) -> dict:
    cache_key = f"purchased_orders:{user.id}:{skip}:{limit}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        logger.info(f"Cache hit for key={cache_key}")
        return json.loads(cached_data)
    
    logger.info(f"Cache miss for key={cache_key}")
    # Single query fetching both total count and orders using a window function
    query = (
        select(PurchasedOrders, func.count().over().label('total'))
        .where(PurchasedOrders.user_id == user.id)
        .order_by(PurchasedOrders.timestamp.desc())
    )
    result = await db.execute(query.offset(skip).limit(limit))
    rows = result.all()

    if rows:
        total = rows[0][1]  # Total count from the window function
        purchased_orders = [row[0] for row in rows]  # Extract PurchasedOrders objects
    else:
        total = 0
        purchased_orders = []

    orders_list = [
        {
            "id": str(order.id),
            "user_id": str(order.user_id),
            "tick_id": str(order.tick_id),
            "purchase_price": order.purchase_price,
            "purchase_qty": order.purchase_qty,
            "timestamp": order.timestamp.isoformat()
        }
        for order in purchased_orders
    ]
    result_dict = {
        "orders": orders_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }
    
    # Cache the result in Redis with an expiration time of 5 minutes (300 seconds)
    redis_client.setex(cache_key, 300, json.dumps(result_dict))
    logger.info(f"Data cached for key={cache_key}")
    
    return result_dict