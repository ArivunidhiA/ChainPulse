"""
ChainPulse FastAPI app: API + APScheduler (indexer, dbt, analysis).
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.connection import init_connection_pool, close_connection_pool
from api.routes import router as api_router
from scheduler.jobs import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_connection_pool()
    sched = start_scheduler()
    yield
    sched.shutdown(wait=False)
    close_connection_pool()


app = FastAPI(
    title="ChainPulse API",
    description="On-chain DeFi analytics pipeline",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/")
def root():
    return {"service": "ChainPulse", "docs": "/docs"}
