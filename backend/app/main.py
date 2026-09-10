import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.schemas import HealthCheckResponse
from app.routers import facilities, inventory, forecast, redistribution, insights, federation

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade API for predicting medicine stock-outs, recommending cross-facility redistribution, and providing GenAI clinical logistics insights.",
)


@app.on_event("startup")
def startup_event():
    if not settings.GEMINI_API_KEY:
        if settings.ENVIRONMENT == "production":
            logger.error("CRITICAL: GEMINI_API_KEY environment variable is not set! GenAI features will fallback to deterministic rules.")
        else:
            logger.warning("GEMINI_API_KEY is not set. GenAI insights will use fallback responses during local development.")
    else:
        logger.info("GEMINI_API_KEY successfully loaded from environment.")


# Strict CORS Middleware configuration (restricted allowed origins, no wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include Subsystem Routers
app.include_router(facilities.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(forecast.router, prefix=settings.API_V1_STR)
app.include_router(redistribution.router, prefix=settings.API_V1_STR)
app.include_router(insights.router, prefix=settings.API_V1_STR)
app.include_router(federation.router, prefix=settings.API_V1_STR)


@app.get("/health", response_model=HealthCheckResponse, tags=["Health Check"])
async def health_check():
    """System health status check."""
    return HealthCheckResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )
