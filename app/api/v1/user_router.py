from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.v1.user_service import signup, login
from app.middleware.jwt import JWTHandler
from app.middleware.logger import get_logger

# Initialize API router for user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])

# Initialize logger for tracking API requests
logger = get_logger()

@router.post("/signup", response_model=Token)
async def signup_endpoint(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    API endpoint for user signup.
    """
    logger.info(f"API request to signup user with email={user.email}")
    try:
        result = await signup(db, user)
        logger.info(f"User signed up successfully: {user.email}")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token)
async def login_endpoint(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    API endpoint for user login.
    """
    logger.info(f"API request to login user with email={user.email}")
    try:
        result = await login(db, user)
        logger.info(f"User logged in successfully: {user.email}")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout_endpoint(authorization: str = Header(...)):
    """
    API endpoint for user logout. Invalidates the provided JWT token.
    """
    logger.info("API request to logout user")
    try:
        # Extract token from Authorization header (expects "Bearer <token>")
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=400, detail="Invalid authorization header")
        
        token = authorization.split(" ")[1]
        
        # Blacklist the token
        JWTHandler.blacklist_token(token)
        logger.info("User logged out successfully")
        return {"message": "Successfully logged out"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))