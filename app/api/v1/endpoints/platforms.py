"""
Эндпоинты для работы с платформами и валидации ссылок.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import HttpUrl

from app.models.schemas import (
    SupportedPlatformsResponse, URLValidationResponse, 
    PlatformInfo, Platform
)
from app.services.url_validator import URLValidator
from app.services.video_downloader import VideoDownloader

router = APIRouter()

# Сервисы
url_validator = URLValidator()
video_downloader = VideoDownloader()


@router.get("/supported", response_model=SupportedPlatformsResponse, summary="Поддерживаемые платформы")
async def get_supported_platforms():
    """
    Получение списка поддерживаемых платформ для транскрипции.
    
    Возвращает информацию о каждой платформе:
    - Название и домены
    - Поддерживаемые форматы
    - Максимальная длительность
    - Дополнительные возможности
    """
    platforms = [
        PlatformInfo(
            name="YouTube",
            domains=["youtube.com", "youtu.be", "m.youtube.com"],
            supported_formats=["MP4", "WebM", "3GP"],
            max_duration=7200,  # 2 часа в секундах
            features=[
                "Высокое качество видео",
                "Субтитры (если доступны)",
                "Различные разрешения",
                "Поддержка плейлистов",
                "Обработка возрастных ограничений"
            ]
        ),
        PlatformInfo(
            name="Instagram",
            domains=["instagram.com", "www.instagram.com"],
            supported_formats=["MP4"],
            max_duration=3600,  # 1 час
            features=[
                "Посты с видео",
                "IGTV",
                "Reels",
                "Stories (публичные)"
            ]
        ),
        PlatformInfo(
            name="ВКонтакте",
            domains=["vk.com", "vkontakte.ru", "m.vk.com"],
            supported_formats=["MP4", "WebM"],
            max_duration=7200,  # 2 часа
            features=[
                "Видеозаписи пользователей",
                "Видео сообществ",
                "Различные качества",
                "Публичные видео"
            ]
        ),
        PlatformInfo(
            name="TikTok",
            domains=["tiktok.com", "www.tiktok.com", "m.tiktok.com"],
            supported_formats=["MP4"],
            max_duration=600,  # 10 минут
            features=[
                "Короткие видео",
                "Музыкальный контент",
                "Вертикальный формат",
                "Без водяных знаков"
            ]
        )
    ]
    
    return SupportedPlatformsResponse(platforms=platforms)


@router.post("/validate", response_model=URLValidationResponse, summary="Валидация URL")
async def validate_url(url: HttpUrl):
    """
    Валидация URL видео и получение базовой информации.
    
    Проверяет:
    - Поддерживается ли платформа
    - Доступность видео
    - Базовые метаданные (если возможно)
    
    Не выполняет полное скачивание видео.
    """
    try:
        # Валидация URL
        validation_result = await url_validator.validate_url(str(url))
        
        if not validation_result.is_valid:
            return URLValidationResponse(
                is_valid=False,
                reason=validation_result.reason
            )
        
        # Получение метаданных без скачивания
        try:
            metadata = await video_downloader.get_video_info(str(url))
            
            return URLValidationResponse(
                is_valid=True,
                platform=validation_result.platform,
                metadata=metadata
            )
            
        except Exception as meta_error:
            # URL валиден, но не удалось получить метаданные
            return URLValidationResponse(
                is_valid=True,
                platform=validation_result.platform,
                reason=f"URL валиден, но не удалось получить метаданные: {str(meta_error)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при валидации URL: {str(e)}"
        )


@router.get("/info/{platform}", response_model=PlatformInfo, summary="Информация о платформе")
async def get_platform_info(platform: Platform):
    """Получение подробной информации о конкретной платформе."""
    
    platform_data = {
        Platform.YOUTUBE: PlatformInfo(
            name="YouTube",
            domains=["youtube.com", "youtu.be", "m.youtube.com"],
            supported_formats=["MP4", "WebM", "3GP"],
            max_duration=7200,
            features=[
                "Высокое качество видео до 4K",
                "Автоматические субтитры",
                "Различные разрешения (144p-4K)",
                "Поддержка плейлистов",
                "Обработка возрастных ограничений",
                "Поддержка прямых трансляций (завершенных)"
            ]
        ),
        Platform.INSTAGRAM: PlatformInfo(
            name="Instagram",
            domains=["instagram.com", "www.instagram.com"],
            supported_formats=["MP4"],
            max_duration=3600,
            features=[
                "Посты с видео (до 60 минут)",
                "IGTV (длинные видео)",
                "Reels (короткие видео)",
                "Stories (24 часа, только публичные)",
                "Квадратный и вертикальный форматы"
            ]
        ),
        Platform.VKONTAKTE: PlatformInfo(
            name="ВКонтакте",
            domains=["vk.com", "vkontakte.ru", "m.vk.com"],
            supported_formats=["MP4", "WebM"],
            max_duration=7200,
            features=[
                "Видеозаписи пользователей",
                "Видео сообществ и групп",
                "Различные качества (240p-1080p)",
                "Только публичные видео",
                "Поддержка русского контента"
            ]
        ),
        Platform.TIKTOK: PlatformInfo(
            name="TikTok",
            domains=["tiktok.com", "www.tiktok.com", "m.tiktok.com"],
            supported_formats=["MP4"],
            max_duration=600,
            features=[
                "Короткие видео (15 секунд - 10 минут)",
                "Музыкальный и развлекательный контент",
                "Вертикальный формат (9:16)",
                "Скачивание без водяных знаков",
                "Поддержка трендовых видео"
            ]
        )
    }
    
    if platform not in platform_data:
        raise HTTPException(status_code=404, detail="Платформа не найдена")
    
    return platform_data[platform]


@router.get("/domains", summary="Список доменов всех платформ")
async def get_all_domains():
    """
    Получение списка всех поддерживаемых доменов.
    
    Полезно для автоматического определения платформы по URL.
    """
    domains = {
        "youtube": ["youtube.com", "youtu.be", "m.youtube.com"],
        "instagram": ["instagram.com", "www.instagram.com"],
        "vkontakte": ["vk.com", "vkontakte.ru", "m.vk.com"],
        "tiktok": ["tiktok.com", "www.tiktok.com", "m.tiktok.com"]
    }
    
    # Плоский список всех доменов
    all_domains = []
    for platform_domains in domains.values():
        all_domains.extend(platform_domains)
    
    return {
        "domains_by_platform": domains,
        "all_domains": sorted(all_domains),
        "total_domains": len(all_domains)
    }