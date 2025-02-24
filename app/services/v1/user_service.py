from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.users import Users
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from passlib.context import CryptContext
from fastapi import HTTPException
from app.middleware.jwt import JWTHandler
from app.middleware.logger import get_logger

# Initialize logger for tracking user-related operations
logger = get_logger()

# Password hashing context using bcrypt for security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: AsyncSession, user: UserCreate) -> UserResponse:
    """
    Create a new user in the database if the email is not already registered.
    """
    logger.info(f"Creating user with email={user.email}")

    # Check if a user with the same email already exists
    result = await db.execute(select(Users).where(Users.email == user.email))
    if result.scalar_one_or_none():
        logger.error(f"Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before storing it
    hashed_password = pwd_context.hash(user.password)

    # Create a new user instance and store it in the database
    db_user = Users(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    logger.info(f"User created with id={db_user.id}")
    return UserResponse.from_orm(db_user)

async def authenticate_user(db: AsyncSession, user: UserLogin) -> Users:
    """
    Authenticate a user by verifying their email and password.
    """
    logger.info(f"Authenticating user with email={user.email}")

    # Fetch the user record from the database
    result = await db.execute(select(Users).where(Users.email == user.email))
    db_user = result.scalar_one_or_none()

    # Validate the user exists and the password matches
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        logger.error(f"Invalid email or password for email={user.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    logger.info(f"User authenticated: {db_user.email}")
    return db_user

async def signup(db: AsyncSession, user: UserCreate) -> Token:
    """
    Handle user signup by creating an account and generating an access token.
    """
    # Create a new user
    db_user = await create_user(db, user)

    # Generate JWT access token
    access_token = JWTHandler.create_access_token(data={"sub": str(db_user.id)})

    logger.info(f"User signed up and token issued for email={db_user.email}")
    return Token(access_token=access_token)

async def login(db: AsyncSession, user: UserLogin) -> Token:
    """
    Handle user login by verifying credentials and generating an access token.
    """
    # Authenticate the user
    db_user = await authenticate_user(db, user)

    # Generate JWT access token
    access_token = JWTHandler.create_access_token(data={"sub": str(db_user.id)})

    logger.info(f"User logged in and token issued for email={db_user.email}")
    return Token(access_token=access_token)
