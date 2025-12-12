from backend.routers import suggest
from backend.zenn import generate
from core.logger import logger
from fastapi import FastAPI
from backend.zenn import publish

app = FastAPI(
    title="Zenn Publisher API",
    description="API for generating and publishing Zenn articles",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Zenn Publisher API is running", "version": "1.0.0"}


app.include_router(generate.router)
app.include_router(publish.router)
app.include_router(suggest.router)

logger.info("FastAPI application started successfully")
