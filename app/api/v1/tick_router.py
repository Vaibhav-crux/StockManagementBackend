from fastapi import APIRouter, Depends, Query, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.v1.tick_service import get_tickers, get_orders_by_tick_id, get_ohlc_data
from app.schemas.tick import TickerSearchResponse, OrderDetailsResponse
from typing import Optional, List
import uuid
from datetime import datetime
import asyncio
from app.middleware.websocket_manager import websocket_manager
from app.middleware.logger import get_logger
from datetime import date
from fastapi import Query
from app.schemas.tick import OHLCResponse

router = APIRouter(tags=["ticks"])
logger = get_logger()

def parse_date(date_str: str) -> date:
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Use DD-MM-YYYY")
        raise HTTPException(
            status_code=422,
            detail="Invalid date format. Use DD-MM-YYYY (e.g., 05-04-2022)"
        )

@router.get("/tickers", response_model=TickerSearchResponse)
async def get_tickers_endpoint(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None),
    start_date: Optional[str] = Query(None, description="Start date for filtering (DD-MM-YYYY)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (DD-MM-YYYY)")
):
    logger.info(f"API request to get tickers with skip={skip}, limit={limit}, search={search}")
    try:
        start_date_parsed = parse_date(start_date) if start_date else None
        end_date_parsed = parse_date(end_date) if end_date else None
        tickers, total, current_skip, current_limit = await get_tickers(
            db, skip=skip, limit=limit, search=search, start_date=start_date_parsed, end_date=end_date_parsed
        )
        logger.info(f"Returning {len(tickers)} tickers")
        return TickerSearchResponse(
            tickers_with_dates=tickers,
            total=total,
            skip=current_skip,
            limit=current_limit
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching tickers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickers/{tick_id}", response_model=OrderDetailsResponse)
async def get_orders_by_tick_id_endpoint(
    tick_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of orders to return"),
    interval: Optional[int] = Query(None, ge=0, description="Time interval in minutes to filter orders from current time")
):
    logger.info(f"API request to get orders for tick_id={tick_id}")
    orders_data = await get_orders_by_tick_id(db, tick_id, skip=skip, limit=limit, interval=interval)
    if not orders_data:
        logger.warning(f"Ticker not found for tick_id={tick_id}")
        raise HTTPException(status_code=404, detail="Ticker not found")
    logger.info(f"Returning orders for tick_id={tick_id}")
    return OrderDetailsResponse(**orders_data)

@router.websocket("/tickers/ws")
async def websocket_tickers(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    logger.info("WebSocket connection established")
    await websocket_manager.connect(websocket)
    try:
        while True:
            try:
                tickers, total, skip, limit = await get_tickers(db)
                tickers_dict = [ticker.model_dump(mode='json') for ticker in tickers]
                # Log the first few tickers to confirm order
                logger.debug(f"WebSocket broadcast tickers (first 3): {tickers_dict[:3]}")
                await websocket_manager.broadcast({
                    "tickers_with_dates": tickers_dict,
                    "total": total,
                    "skip": skip,
                    "limit": limit
                })
                logger.debug("WebSocket broadcast sent")
                await asyncio.sleep(5)
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                logger.error(f"WebSocket broadcast error: {str(e)}")
                break
    finally:
        try:
            websocket_manager.disconnect(websocket)
            logger.info("WebSocket connection closed")
        except ValueError:
            pass

@router.get("/ohlc", response_model=List[OHLCResponse])
async def get_ohlc_endpoint(
    ticker: str = Query(..., description="Ticker symbol to fetch OHLC data for"),
    start_date: Optional[str] = Query(None, description="Start date for filtering (DD-MM-YYYY)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (DD-MM-YYYY)"),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"API request to get OHLC data for ticker={ticker}")
    try:
        start_date_parsed = parse_date(start_date) if start_date else None
        end_date_parsed = parse_date(end_date) if end_date else None
        ohlc_data = await get_ohlc_data(db, ticker, start_date_parsed, end_date_parsed)
        logger.info(f"Returning OHLC data for ticker={ticker}")
        return ohlc_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching OHLC data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))