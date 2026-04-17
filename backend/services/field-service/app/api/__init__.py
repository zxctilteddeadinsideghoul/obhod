from fastapi import APIRouter

from app.api.routes.field import router as field_router


api_router = APIRouter()
api_router.include_router(field_router)
