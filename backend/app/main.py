"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.models.schemas import HealthResponse
from app.routers import devices, diagnostics, scenes
from app.services.ha_client import ha_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LG Hue Automation API")
    yield
    logger.info("Shutting down — closing HA client")
    await ha_client.close()


app = FastAPI(
    title="LG Hue Automation API",
    description="Control LG TV picture modes and Philips Hue lights with one click.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again shortly."},
    )


# In production, Nginx proxies everything through port 80 (same origin).
# CORS is only needed during local development with split ports.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list or ["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(scenes.router)
app.include_router(devices.router)
app.include_router(diagnostics.router)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    ha_connected = await ha_client.is_connected()
    return HealthResponse(
        status="healthy" if ha_connected else "degraded",
        version="1.0.0",
        ha_connected=ha_connected,
    )
