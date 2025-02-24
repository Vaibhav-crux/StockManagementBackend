from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from collections import defaultdict
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.clients = defaultdict(lambda: {'count': 0, 'start_time': time.time()})
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        client_data = self.clients[client_ip]
        current_time = time.time()
        
        # Reset the counter if the time window has passed
        if current_time - client_data['start_time'] > self.window:
            client_data['count'] = 0
            client_data['start_time'] = current_time
        
        # Check rate limit
        if client_data['count'] >= self.limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        
        client_data['count'] += 1
        response = await call_next(request)
        return response

def setup_rate_limit(app, limit: int = 100, window: int = 60):
    app.add_middleware(RateLimitMiddleware, limit=limit, window=window)
