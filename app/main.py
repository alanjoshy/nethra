from importlib.metadata import version
from fastapi import FastAPI 
from app.api.health import router as health_router 


app = FastAPI(
    title="Nethra Backend API",
    version="0.1.0",
    description="Backend API for Nethra application"
    )

app.include_router(health_router) 