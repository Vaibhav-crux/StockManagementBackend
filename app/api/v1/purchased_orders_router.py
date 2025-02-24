from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.v1.purchased_orders_service import place_order, get_purchased_orders_by_user, get_current_user
from app.schemas.purchased_order import PurchasedOrderCreate, PurchasedOrderResponse, PurchasedOrdersResponse
from typing import List
from fastapi.security import OAuth2PasswordBearer
from app.middleware.logger import get_logger

router = APIRouter(tags=["orders"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")
logger = get_logger()

@router.post("/place-order", response_model=List[PurchasedOrderResponse])
async def place_order_endpoint(
    orders: List[PurchasedOrderCreate],
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        logger.info(f"Received request to place {len(orders)} orders for token: {token[:8]}...")
        result = [await place_order(db, order, token) for order in orders]
        logger.info(f"Successfully placed {len(result)} orders")
        return result
    except HTTPException as e:
        logger.error(f"HTTP exception while placing orders: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while placing orders: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/purchased", response_model=PurchasedOrdersResponse)
async def get_purchased_orders_endpoint(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of orders to return")
):
    try:
        logger.info(f"Fetching purchased orders - skip: {skip}, limit: {limit}, token: {token[:8]}...")
        user = await get_current_user(token, db)
        result = PurchasedOrdersResponse(**await get_purchased_orders_by_user(db, user, skip=skip, limit=limit))
        logger.info(f"Successfully retrieved {len(result.orders)} purchased orders for user: {user.id}")
        return result
    except HTTPException as e:
        logger.error(f"HTTP exception while fetching purchased orders: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while fetching purchased orders: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))