from fastapi import FastAPI
from app.api.v1.tick_router import router as tick_router
from app.api.v1.user_router import router as user_router
from app.api.v1.purchased_orders_router import router as order_router
from app.api.v1.portfolio_router import router as portfolio_router
from app.api.v1.quality_check_router import router as quality_check
from app.middleware.cors import setup_cors
from app.middleware.gzip import setup_gzip
from app.middleware.timeout import setup_timeout
from app.middleware.logger import get_logger
from app.middleware.rate_limit import setup_rate_limit
from app.middleware.error_handler import error_handler

app = FastAPI()
logger = get_logger()

# Setup middleware
setup_cors(app)
setup_gzip(app)
setup_timeout(app, timeout=10)
setup_rate_limit(app, limit=100, window=60) 
app.middleware("http")(error_handler)

prefix_endpoint = "/api/v1"
app.include_router(tick_router, prefix=prefix_endpoint)
app.include_router(user_router, prefix=prefix_endpoint)
app.include_router(order_router, prefix=prefix_endpoint)
app.include_router(portfolio_router, prefix=prefix_endpoint)
app.include_router(quality_check, prefix=prefix_endpoint)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Server is up and running!"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "message": "All services are running"}