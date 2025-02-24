import asyncio
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException
from app.middleware.logger import get_logger

logger = get_logger()

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout: int = 30):
        """
        Initialize the timeout middleware with a default timeout of 30 seconds
        :param app: FastAPI application instance
        :param timeout: Maximum time in seconds for request processing
        """
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Dispatch the request with timeout handling
        :param request: Incoming request
        :param call_next: Next middleware or endpoint handler
        :return: Response
        """
        try:
            # Log the request start
            logger.info(f"Processing request: {request.method} {request.url.path}")
            
            # Execute the request with timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout
            )
            
            # Log successful completion
            logger.info(f"Completed request: {request.method} {request.url.path}")
            return response
            
        except asyncio.TimeoutError:
            # Log timeout error
            logger.error(f"Request timeout after {self.timeout}s: {request.method} {request.url.path}")
            raise HTTPException(
                status_code=504,
                detail=f"Request timed out after {self.timeout} seconds"
            )
        except Exception as e:
            # Log any other errors
            logger.error(f"Error processing request {request.method} {request.url.path}: {str(e)}")
            raise

def setup_timeout(app, timeout: int = 10):
    """
    Helper function to add timeout middleware to the FastAPI app
    :param app: FastAPI application instance
    :param timeout: Timeout value in seconds
    """
    app.add_middleware(TimeoutMiddleware, timeout=timeout)
    logger.info(f"Timeout middleware configured with {timeout}s timeout")