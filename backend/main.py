from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.routers import suggest
from backend.zenn import generate
from backend.core.logger import configure_logging, get_logger
from backend.zenn import publish
from backend.core.database import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(level="DEBUG")
    logger = get_logger(__name__)
    database.create_tables()

    logger.info("Connected to DataBase")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="Zenn Publisher API",
    description="API for generating and publishing Zenn articles",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Zenn Publisher API is running", "version": "1.0.0"}


app.include_router(generate.router)
app.include_router(publish.router)
app.include_router(suggest.router)

logger = get_logger(__name__)
logger.info("FastAPI application started successfully")
