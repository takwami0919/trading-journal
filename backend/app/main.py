from fastapi import FastAPI

from app.core.config import settings
from app.api.trades import router as trades_router
from app.api.executions import router as executions_router
from app.api.analytics import router as analytics_router

app = FastAPI(title=settings.APP_NAME)

app.include_router(trades_router)
app.include_router(executions_router)
app.include_router(analytics_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "environment": settings.ENVIRONMENT}