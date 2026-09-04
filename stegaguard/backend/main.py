"""StegaGuard API — AI Model Weight Integrity Scanner."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import scan as scan_router
from routers import report as report_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("stegaguard")

app = FastAPI(
    title="StegaGuard API",
    description="AI Model Weight Integrity Scanner",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — permissive for dev; lock down origins before production.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(scan_router.router, prefix="/api")
app.include_router(report_router.router, prefix="/api")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Startup event
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    logger.info("StegaGuard API started")
