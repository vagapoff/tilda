"""
Главный роутер API v1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import transcription, platforms, health

api_router = APIRouter()

# Подключение эндпоинтов
api_router.include_router(
    transcription.router, 
    prefix="/transcribe", 
    tags=["transcription"]
)

api_router.include_router(
    platforms.router, 
    prefix="/platforms", 
    tags=["platforms"]
)

api_router.include_router(
    health.router, 
    tags=["health"]
)