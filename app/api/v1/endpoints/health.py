"""
Эндпоинты для проверки здоровья системы.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import os

from app.models.schemas import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Проверка здоровья сервиса")
async def health_check():
    """Базовая проверка здоровья сервиса."""
    return HealthResponse(
        status="healthy",
        service="video-transcription-agent",
        version="1.0.0"
    )


@router.get("/health/detailed", summary="Подробная проверка здоровья")
async def detailed_health_check():
    """
    Подробная проверка здоровья системы.
    
    Включает информацию о:
    - Состоянии сервиса
    - Использовании ресурсов
    - Доступности зависимостей
    - Состоянии файловой системы
    """
    try:
        # Основная информация
        health_data = {
            "service": "video-transcription-agent",
            "version": "1.0.0",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT
        }
        
        # Системные ресурсы
        try:
            health_data["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            health_data["system"] = {"error": f"Не удалось получить системную информацию: {str(e)}"}
        
        # Проверка директорий
        directories_status = {}
        for dir_name, dir_path in [
            ("uploads", settings.UPLOAD_DIR),
            ("temp", settings.TEMP_DIR)
        ]:
            try:
                if os.path.exists(dir_path):
                    stat = os.statvfs(dir_path)
                    directories_status[dir_name] = {
                        "exists": True,
                        "writable": os.access(dir_path, os.W_OK),
                        "free_space": stat.f_bavail * stat.f_frsize
                    }
                else:
                    directories_status[dir_name] = {
                        "exists": False,
                        "error": "Directory does not exist"
                    }
            except Exception as e:
                directories_status[dir_name] = {
                    "error": str(e)
                }
        
        health_data["directories"] = directories_status
        
        # Проверка ML модели (базовая)
        try:
            import whisper
            health_data["ml"] = {
                "whisper_available": True,
                "model": settings.WHISPER_MODEL,
                "device": settings.DEVICE
            }
        except Exception as e:
            health_data["ml"] = {
                "whisper_available": False,
                "error": str(e)
            }
        
        # Проверка зависимостей для скачивания видео
        dependencies_status = {}
        
        # yt-dlp
        try:
            import yt_dlp
            dependencies_status["yt_dlp"] = {
                "available": True,
                "version": yt_dlp.version.__version__
            }
        except Exception as e:
            dependencies_status["yt_dlp"] = {
                "available": False,
                "error": str(e)
            }
        
        # FFmpeg
        try:
            import ffmpeg
            dependencies_status["ffmpeg"] = {"available": True}
        except Exception as e:
            dependencies_status["ffmpeg"] = {
                "available": False,
                "error": str(e)
            }
        
        health_data["dependencies"] = dependencies_status
        
        # Определение общего статуса
        critical_issues = []
        
        # Проверка критичных компонентов
        if not dependencies_status.get("yt_dlp", {}).get("available"):
            critical_issues.append("yt-dlp недоступен")
        
        if not health_data.get("ml", {}).get("whisper_available"):
            critical_issues.append("Whisper недоступен")
        
        # Проверка места на диске
        system_info = health_data.get("system", {})
        if isinstance(system_info.get("disk"), dict):
            disk_usage = system_info["disk"].get("percent", 0)
            if disk_usage > 90:
                critical_issues.append(f"Диск заполнен на {disk_usage}%")
        
        # Проверка памяти
        if isinstance(system_info.get("memory"), dict):
            memory_usage = system_info["memory"].get("percent", 0)
            if memory_usage > 90:
                critical_issues.append(f"Память заполнена на {memory_usage}%")
        
        if critical_issues:
            health_data["status"] = "degraded"
            health_data["issues"] = critical_issues
        else:
            health_data["status"] = "healthy"
        
        return health_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при проверке здоровья системы: {str(e)}"
        )


@router.get("/health/ready", summary="Проверка готовности к работе")
async def readiness_check():
    """
    Проверка готовности сервиса к обработке запросов.
    
    Возвращает 200 если сервис готов, 503 если нет.
    """
    try:
        ready = True
        issues = []
        
        # Проверка критичных зависимостей
        try:
            import whisper
        except ImportError:
            ready = False
            issues.append("Whisper не установлен")
        
        try:
            import yt_dlp
        except ImportError:
            ready = False
            issues.append("yt-dlp не установлен")
        
        # Проверка директорий
        for dir_name, dir_path in [
            ("uploads", settings.UPLOAD_DIR),
            ("temp", settings.TEMP_DIR)
        ]:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception:
                    ready = False
                    issues.append(f"Не удалось создать директорию {dir_name}")
            elif not os.access(dir_path, os.W_OK):
                ready = False
                issues.append(f"Нет прав записи в директорию {dir_name}")
        
        if ready:
            return {
                "status": "ready",
                "message": "Сервис готов к обработке запросов",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "not_ready",
                    "issues": issues,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при проверке готовности: {str(e)}"
        )


@router.get("/health/live", summary="Проверка живости сервиса")
async def liveness_check():
    """
    Простая проверка живости сервиса.
    
    Используется для проверки того, что приложение запущено и отвечает.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "video-transcription-agent"
    }