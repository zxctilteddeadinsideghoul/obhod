from fastapi import APIRouter

from app.api.routes.reports import router as reports_router


api_router = APIRouter()
api_router.include_router(reports_router)
