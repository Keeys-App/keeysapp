from fastapi import APIRouter
from .locales import router as locales_router

api_router = APIRouter()
api_router.include_router(locales_router, prefix="/locales", tags=["locales"])
