from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from api.endpoints import photos, users
from core.config import settings
from infrastructure.database import init_db

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Photo Management System API",
    version="1.0.0",
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(photos.router, prefix=f"{settings.API_PREFIX}/photos", tags=["photos"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["users"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
