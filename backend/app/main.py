from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for predicting medicine stock-outs and recommending cross-facility redistribution across PHCs.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get(f"{settings.API_V1_STR}/summary", tags=["Dashboard Summary"])
async def get_dashboard_summary():
    return {
        "total_phcs": 142,
        "predicted_stockouts_30d": 18,
        "active_redistributions": 7,
        "essential_medicines_monitored": 54,
    }
