from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.v1.portfolio_service import calculate_portfolio_positions
from app.schemas.portfolio import PortfolioResponse
from fastapi.security import OAuth2PasswordBearer
from app.middleware.logger import get_logger
from app.middleware.jwt import JWTHandler
import uuid


router = APIRouter(tags=["portfolio"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")
logger = get_logger()

@router.post("/portfolio-position", response_model=PortfolioResponse)
async def get_portfolio_position(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    API endpoint to retrieve the user's portfolio position based on their purchased orders.
    """
    try:
        logger.info("Fetching portfolio position")
        
        # Decode the JWT token to extract user information
        payload = JWTHandler.decode_token(token)
        user_id = uuid.UUID(payload.get("sub"))

        # Calculate portfolio positions for the authenticated user
        result = await calculate_portfolio_positions(db, user_id)
        logger.info(f"Successfully retrieved portfolio for user_id={user_id}")
        return result
    except HTTPException as e:
        logger.error(f"HTTP exception while fetching portfolio: {str(e)}")
        raise e  # Re-raise the HTTP exception
    except Exception as e:
        logger.error(f"Unexpected error while fetching portfolio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))  # Return a generic server error
