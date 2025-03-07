from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from collections import defaultdict
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on incoming requests.
    Limits the number of requests from a single IP address within a given time window.
    """
    def __init__(self, app, limit: int = 100, window: int = 60):
        """
        Initializes the rate limiter.
        """
        super().__init__(app)
        self.limit = limit
        self.window = window
        # Dictionary to track request counts and start times for each client IP
        self.clients = defaultdict(lambda: {'count': 0, 'start_time': time.time()})
    
    async def dispatch(self, request: Request, call_next):
        """
        Intercepts incoming requests and applies rate limiting.
        """
        client_ip = request.client.host  # Get the client's IP address
        client_data = self.clients[client_ip]
        current_time = time.time()
        
        # Reset the request count if the time window has elapsed
        if current_time - client_data['start_time'] > self.window:
            client_data['count'] = 0
            client_data['start_time'] = current_time
        
        # If request count exceeds the limit, return a 429 Too Many Requests error
        if client_data['count'] >= self.limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        
        # Increment request count for the client
        client_data['count'] += 1
        
        # Process the request and return the response
        response = await call_next(request)
        return response

def setup_rate_limit(app, limit: int = 100, window: int = 60):
    """
    Helper function to add the rate limit middleware to a FastAPI application.
    """
    app.add_middleware(RateLimitMiddleware, limit=limit, window=window)
