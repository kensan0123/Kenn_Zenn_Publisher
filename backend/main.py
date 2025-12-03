from fastapi import FastAPI
from routers import generate

app = FastAPI()

app.include_router(generate.router)
