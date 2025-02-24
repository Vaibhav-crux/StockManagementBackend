from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv
from app.middleware.logger import get_logger

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", 30))
logger = get_logger()

# In-memory blacklist for invalidated tokens (replace with Redis or DB in production)
TOKEN_BLACKLIST = set()

class JWTHandler:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        # Create a new JWT access token
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRY_MINUTES))
        to_encode.update({"exp": expire})
        try:
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            logger.debug(f"Created access token for user_id={data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(status_code=500, detail="Could not create access token")

    @staticmethod
    def decode_token(token: str) -> dict:
        # Decode and verify a JWT token
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # Check if token is blacklisted
            if token in TOKEN_BLACKLIST:
                logger.error("Attempt to use blacklisted token")
                raise credentials_exception
            
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                logger.error("No user_id in token payload")
                raise credentials_exception
            return payload
        except JWTError as e:
            logger.error(f"JWT decoding error: {str(e)}")
            raise credentials_exception

    @staticmethod
    def blacklist_token(token: str) -> None:
        # Add token to blacklist
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if "exp" in payload:
                TOKEN_BLACKLIST.add(token)
                logger.info(f"Token blacklisted for user_id={payload.get('sub')}")
            else:
                logger.warning("Token without expiry provided for blacklisting")
        except JWTError as e:
            logger.error(f"Invalid token for blacklisting: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid token")