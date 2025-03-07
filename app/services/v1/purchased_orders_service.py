from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException, status
from app.db.models.purchased_orders import PurchasedOrders
from app.db.models.ticks import Ticks
from app.db.models.users import Users
from app.schemas.purchased_order import PurchasedOrderCreate, PurchasedOrderResponse, PurchasedOrdersResponse
from app.middleware.jwt import JWTHandler
from app.middleware.logger import get_logger
from app.config.redis_client_connection import redis_client
from datetime import datetime
import uuid
import json
from sqlalchemy.orm import joinedload

logger = get_logger()

async def get_current_user(token: str, db: AsyncSession):
    logger.info("Validating user token")
    payload = JWTHandler.decode_token(token)
    user_id = payload.get("sub")

    result = await db.execute(select(Users).filter(Users.id == uuid.UUID(user_id)))
    user = result.scalars().first()

    if user is None:
        logger.warning(f"No user found for user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"User authenticated: {user.email}")
    return user

async def place_purchased_order(db: AsyncSession, order: PurchasedOrderCreate, user_id: uuid.UUID) -> PurchasedOrderResponse:
    # Fetch the tick with its latest order
    result = await db.execute(
        select(Ticks)
        .filter(Ticks.id == order.tick_id)
        .options(joinedload(Ticks.latest_order))
    )
    tick = result.scalars().first()

    if not tick:
        logger.error(f"Ticker not found for tick_id={order.tick_id}")
        raise HTTPException(status_code=404, detail="Ticker not found")

    # Allow the first order to proceed even if no latest_order exists (initial case)
    latest_order = tick.latest_order
    if latest_order and latest_order.ltq < order.purchase_qty:
        logger.error(f"Not enough quantity available for tick_id={order.tick_id}. Requested: {order.purchase_qty}, Available: {latest_order.ltq}")
        raise HTTPException(status_code=400, detail="Not enough quantity available for purchase")

    # Create a new purchased order
    db_order = PurchasedOrders(
        user_id=user_id,
        tick_id=order.tick_id,
        purchase_price=order.purchase_price,
        purchase_qty=order.purchase_qty
    )

    # Create a new order with updated ltq (default to full qty if no previous order)
    from app.db.models.orders import Orders
    new_order = Orders(
        timestamp=func.now(),
        ltp=latest_order.ltp if latest_order else 0.0,
        buyprice=latest_order.buyprice if latest_order else 0.0,
        buyqty=latest_order.buyqty if latest_order else 0,
        sellprice=latest_order.sellprice if latest_order else 0.0,
        sellqty=latest_order.sellqty if latest_order else 0,
        ltq=(latest_order.ltq - order.purchase_qty) if latest_order else order.purchase_qty,
        openinterest=latest_order.openinterest if latest_order else 0,
        tick_id=order.tick_id
    )

    # Add entities to the session
    db.add(db_order)
    db.add(new_order)

    # Explicitly flush to generate IDs without committing yet
    await db.flush()

    # Pre-fetch all attributes before commit
    db_order_id = db_order.id
    new_order_id = new_order.id
    remaining_quantity = new_order.ltq
    user_id_str = str(db_order.user_id)
    tick_id_str = str(db_order.tick_id)
    purchase_price = db_order.purchase_price
    purchase_qty = db_order.purchase_qty
    timestamp_str = db_order.timestamp.isoformat() if db_order.timestamp else datetime.now().isoformat()
    tick_id = tick.id

    # Update tick.latest_order_id with the new order ID
    tick.latest_order_id = new_order_id

    # Single commit for all changes
    await db.commit()

    # Refresh and expunge objects to ensure no further lazy loading
    await db.refresh(db_order)
    await db.refresh(new_order)
    await db.refresh(tick)
    db.expunge(db_order)
    db.expunge(new_order)
    db.expunge(tick)

    # Log using pre-fetched values
    logger.info(f"Purchased order recorded with id={db_order_id}. New order created with id={new_order_id}, remaining quantity: {remaining_quantity}")
    logger.info(f"Updated tick.latest_order_id to {new_order_id} for tick_id={tick_id}")

    # Invalidate cache
    cache_key_pattern = f"purchased_orders:{user_id}:*"
    cache_keys = redis_client.keys(cache_key_pattern)
    if cache_keys:
        redis_client.delete(*cache_keys)
        logger.info(f"Cache invalidated for keys: {cache_keys}")

    # Return response using pre-fetched values
    return PurchasedOrderResponse(
        id=str(db_order_id),
        user_id=user_id_str,
        tick_id=tick_id_str,
        purchase_price=purchase_price,
        purchase_qty=purchase_qty,
        timestamp=timestamp_str,
        ticker=tick.ticker
    )

async def get_purchased_orders_by_user(db: AsyncSession, user: Users, skip: int = 0, limit: int = 100) -> PurchasedOrdersResponse:
    cache_key = f"purchased_orders:{user.id}:{skip}:{limit}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        try:
            logger.info(f"Cache hit for key={cache_key}")
            # Deserialize the cached data
            cached_dict = json.loads(cached_data)
            # Ensure ticker is present in cached orders; if not, invalidate cache and refetch
            for order in cached_dict.get("orders", []):
                if "ticker" not in order:
                    logger.info(f"Invalidating cache for key={cache_key} due to missing ticker field")
                    redis_client.delete(cache_key)
                    cached_data = None
                    break
            if cached_data:
                return PurchasedOrdersResponse(**cached_dict)
        except Exception as e:
            logger.warning(f"Failed to deserialize cached data for key={cache_key}: {str(e)}")
            redis_client.delete(cache_key)
            cached_data = None

    logger.info(f"Cache miss or invalidated for key={cache_key}")

    # Join PurchasedOrders with Ticks to get the ticker name
    query = (
        select(PurchasedOrders, Ticks.ticker)
        .join(Ticks, PurchasedOrders.tick_id == Ticks.id)
        .filter(PurchasedOrders.user_id == user.id)
        .order_by(PurchasedOrders.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()

    # Fetch total count
    total = await db.scalar(select(func.count()).filter(PurchasedOrders.user_id == user.id))

    # Construct response with ticker name
    orders = []
    for row in rows:
        purchased_order = row[0]  # PurchasedOrders object
        ticker = row[1]  # Ticks.ticker value
        # Add ticker as an attribute to the PurchasedOrders object temporarily for from_orm
        purchased_order.ticker = ticker
        order_response = PurchasedOrderResponse.from_orm(purchased_order)
        orders.append(order_response)

    response = PurchasedOrdersResponse(
        orders=orders,
        total=total,
        skip=skip,
        limit=limit
    )

    # Cache the response with the ticker field included
    redis_client.setex(cache_key, 300, json.dumps(response.dict()))
    logger.info(f"Data cached for key={cache_key}")

    return response