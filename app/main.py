from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlmodel import SQLModel

from app.routers import router as books_router
from app.services import populate

INITIAL_DATA = Path("./dataset.sql")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB schema on startup
    await populate()
    yield


app = FastAPI(
    title="Library Management API",
    description="Books Library management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(books_router, prefix=API_PREFIX)
