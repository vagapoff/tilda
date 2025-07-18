"""
Конфигурация приложения.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # Основные настройки
    ENVIRONMENT: str = Field(default="development", description="Режим работы")
    DEBUG: bool = Field(default=True, description="Режим отладки")
    HOST: str = Field(default="0.0.0.0", description="Хост")
    PORT: int = Field(default=8000, description="Порт")
    WORKERS: int = Field(default=4, description="Количество воркеров")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "*"],
        description="Разрешенные хосты"
    )
    
    # База данных
    DATABASE_URL: str = Field(
        default="sqlite:///./transcription.db",
        description="URL базы данных"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL Redis"
    )
    
    # Файловое хранилище
    UPLOAD_DIR: str = Field(default="./uploads", description="Директория загрузок")
    TEMP_DIR: str = Field(default="./temp", description="Временная директория")
    MAX_FILE_SIZE: int = Field(default=2048, description="Максимальный размер файла в МБ")
    CLEANUP_INTERVAL: int = Field(default=3600, description="Интервал очистки в секундах")
    
    # Обработка видео
    MAX_DURATION: int = Field(default=14400, description="Максимальная длительность в секундах (4 часа)")
    MAX_DURATION_URL: int = Field(default=7200, description="Максимальная длительность для ссылок (2 часа)")
    DEFAULT_QUALITY: str = Field(default="720p", description="Качество по умолчанию")
    
    # ML модели
    WHISPER_MODEL: str = Field(default="base", description="Модель Whisper")
    DEVICE: str = Field(default="cpu", description="Устройство для ML (cpu/cuda)")
    BATCH_SIZE: int = Field(default=8, description="Размер батча")
    
    # API ключи (опционально)
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="API ключ OpenAI")
    ASSEMBLYAI_API_KEY: Optional[str] = Field(default=None, description="API ключ AssemblyAI")
    
    # ВКонтакте API
    VK_ACCESS_TOKEN: Optional[str] = Field(default=None, description="Токен доступа ВК")
    
    # Безопасность
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Секретный ключ"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Время жизни токена")
    
    # Статические файлы
    SERVE_STATIC: bool = Field(default=True, description="Раздавать статические файлы")
    
    # Логирование
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")
    LOG_FILE: Optional[str] = Field(default=None, description="Файл логов")
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Валидация окружения."""
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT должен быть development, staging или production")
        return v
    
    @validator("UPLOAD_DIR", "TEMP_DIR")
    def create_directories(cls, v):
        """Создание директорий если они не существуют."""
        os.makedirs(v, exist_ok=True)
        return v
    
    @property
    def is_development(self) -> bool:
        """Проверка режима разработки."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Проверка продакшн режима."""
        return self.ENVIRONMENT == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Создание экземпляра настроек
settings = Settings()