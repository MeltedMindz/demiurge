"""
Demiurge - 3D AI Philosophy Sandbox
Main FastAPI Application Entry Point
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from demiurge.config import settings
from demiurge.api.routes import router as api_router
from demiurge.api.websocket import ConnectionManager, ws_router
from demiurge.orchestration.debate_orchestrator import DebateOrchestrator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("demiurge")

# Global instances
connection_manager = ConnectionManager()
debate_orchestrator: DebateOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown"""
    global debate_orchestrator

    logger.info("Starting Demiurge - 3D AI Philosophy Sandbox")
    logger.info(f"Environment: {settings.environment}")

    # Initialize debate orchestrator
    debate_orchestrator = DebateOrchestrator(connection_manager)

    # Start the debate cycle loop in background
    orchestrator_task = asyncio.create_task(debate_orchestrator.start())

    logger.info("Debate orchestrator started")

    yield

    # Shutdown
    logger.info("Shutting down Demiurge...")
    if debate_orchestrator:
        await debate_orchestrator.stop()
    orchestrator_task.cancel()

    logger.info("Demiurge shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Demiurge",
    description="3D AI Philosophy Sandbox - Where AI agents debate and shape worlds",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)

# Serve static files (images, etc.)
# app.mount("/static", StaticFiles(directory="public"), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Demiurge",
        "description": "3D AI Philosophy Sandbox",
        "version": "1.0.0",
        "status": "running",
        "agents": ["Axioma", "Veridicus", "Paradoxia"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "cycle_duration": settings.cycle_duration_seconds
    }
