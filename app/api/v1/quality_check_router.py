from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.v1.quality_check_service import perform_quality_checks
from app.schemas.quality_check import QualityCheckResponse
from fastapi.security import OAuth2PasswordBearer
from app.middleware.logger import get_logger
from app.middleware.jwt import JWTHandler
import uuid

# Create API router for quality check endpoints
router = APIRouter(tags=["quality_checks"])

# OAuth2 scheme for authentication (expects Bearer Token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

# Initialize logger for tracking API requests
logger = get_logger()

@router.get("/quality-checks", response_model=QualityCheckResponse)
async def get_quality_checks(
    db: AsyncSession = Depends(get_db),  # Dependency injection for database session
    token: str = Depends(oauth2_scheme),  # Extract auth token from request
):
    """
    API endpoint to fetch quality check results for the authenticated user.
    """
    try:
        logger.info("Fetching quality checks")

        # Decode the JWT token to get the user ID
        payload = JWTHandler.decode_token(token)
        user_id = uuid.UUID(payload.get("sub"))

        # Perform quality checks on the user's orders
        result = await perform_quality_checks(db, user_id)
        logger.info(f"Quality checks completed for user_id={user_id}")

        return result  # Return quality check results
    except HTTPException as e:
        logger.error(f"HTTP exception during quality checks: {str(e)}")
        raise e  # Re-raise HTTP exceptions for proper error handling
    except Exception as e:
        logger.error(f"Unexpected error during quality checks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))  # Return generic 500 error for unexpected issues
