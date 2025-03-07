from starlette.middleware.gzip import GZipMiddleware
from app.middleware.logger import get_logger

logger = get_logger()

def setup_gzip(app):
    # Compresses responses larger than 1000 bytes by default.
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("GZip compression middleware enabled with minimum size of 1000 bytes")