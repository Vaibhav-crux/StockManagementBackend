from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError
import logging

logger = logging.getLogger(__name__)

async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)

    except RequestValidationError as e:
        logger.error(f"Validation Error: {e.errors()}")
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "details": e.errors()},
        )

    except SQLAlchemyError as e:
        logger.error(f"Database Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Database error", "details": str(e)},
        )

    except JWTError as e:
        logger.error(f"JWT Authentication Error: {str(e)}")
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"},
        )

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "details": str(e)},
        )
