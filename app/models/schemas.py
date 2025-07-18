"""
Pydantic схемы для API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator


class TaskStatus(str, Enum):
    """Статусы задач."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    COMPLETED = "completed"
    FAILED = "failed"


class SourceType(str, Enum):
    """Типы источников."""
    FILE = "file"
    URL = "url"


class Platform(str, Enum):
    """Поддерживаемые платформы."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    VKONTAKTE = "vkontakte"
    TIKTOK = "tiktok"
    OTHER = "other"


class OutputFormat(str, Enum):
    """Форматы вывода."""
    TXT = "txt"
    SRT = "srt"
    VTT = "vtt"
    JSON = "json"
    DOCX = "docx"


class Language(str, Enum):
    """Поддерживаемые языки."""
    RUSSIAN = "ru"
    ENGLISH = "en"
    AUTO = "auto"


# Базовые модели
class TranscriptionRequest(BaseModel):
    """Запрос на транскрипцию."""
    language: Language = Language.AUTO
    output_format: OutputFormat = OutputFormat.SRT
    include_timestamps: bool = True
    max_line_length: Optional[int] = Field(default=80, ge=20, le=200)
    max_subtitle_duration: Optional[int] = Field(default=5, ge=1, le=10)


class FileUploadRequest(TranscriptionRequest):
    """Запрос на транскрипцию файла."""
    source_type: SourceType = SourceType.FILE


class URLTranscriptionRequest(TranscriptionRequest):
    """Запрос на транскрипцию по URL."""
    url: HttpUrl
    source_type: SourceType = SourceType.URL
    quality: Optional[str] = Field(default="720p", description="Качество видео")
    
    @validator("url")
    def validate_url(cls, v):
        """Валидация URL."""
        url_str = str(v)
        supported_domains = [
            "youtube.com", "youtu.be", "instagram.com", 
            "vk.com", "tiktok.com"
        ]
        
        if not any(domain in url_str for domain in supported_domains):
            raise ValueError("Неподдерживаемая платформа")
        
        return v


# Ответы API
class VideoMetadata(BaseModel):
    """Метаданные видео."""
    title: Optional[str] = None
    duration: Optional[int] = None  # в секундах
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    platform: Optional[Platform] = None
    original_url: Optional[str] = None


class TranscriptionSegment(BaseModel):
    """Сегмент транскрипции."""
    start: float = Field(description="Время начала в секундах")
    end: float = Field(description="Время окончания в секундах")
    text: str = Field(description="Текст сегмента")
    confidence: Optional[float] = Field(default=None, ge=0, le=1)


class TranscriptionResult(BaseModel):
    """Результат транскрипции."""
    text: str = Field(description="Полный текст")
    segments: List[TranscriptionSegment] = Field(description="Сегменты с временными метками")
    language: str = Field(description="Обнаруженный язык")
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    processing_time: Optional[float] = Field(default=None, description="Время обработки в секундах")


class TaskResponse(BaseModel):
    """Ответ с информацией о задаче."""
    task_id: str = Field(description="ID задачи")
    status: TaskStatus = Field(description="Статус задачи")
    source_type: SourceType = Field(description="Тип источника")
    created_at: datetime = Field(description="Время создания")
    updated_at: datetime = Field(description="Время обновления")
    progress: float = Field(default=0.0, ge=0, le=100, description="Прогресс в процентах")
    message: Optional[str] = Field(default=None, description="Сообщение о статусе")
    video_metadata: Optional[VideoMetadata] = Field(default=None)
    result: Optional[TranscriptionResult] = Field(default=None)
    error: Optional[str] = Field(default=None)


class TaskStatusResponse(BaseModel):
    """Краткая информация о статусе задачи."""
    task_id: str
    status: TaskStatus
    progress: float
    message: Optional[str] = None
    error: Optional[str] = None


class PlatformInfo(BaseModel):
    """Информация о платформе."""
    name: str
    domains: List[str]
    supported_formats: List[str]
    max_duration: int  # в секундах
    features: List[str]


class SupportedPlatformsResponse(BaseModel):
    """Список поддерживаемых платформ."""
    platforms: List[PlatformInfo]


class URLValidationResponse(BaseModel):
    """Результат валидации URL."""
    is_valid: bool
    platform: Optional[Platform] = None
    reason: Optional[str] = None
    metadata: Optional[VideoMetadata] = None


class ErrorResponse(BaseModel):
    """Ответ об ошибке."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class HealthResponse(BaseModel):
    """Ответ проверки здоровья."""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Конфигурация экспорта
class ExportConfig(BaseModel):
    """Конфигурация экспорта."""
    format: OutputFormat
    include_timestamps: bool = True
    max_line_length: int = Field(default=80, ge=20, le=200)
    max_subtitle_duration: int = Field(default=5, ge=1, le=10)
    font_size: Optional[int] = Field(default=None, ge=8, le=72)
    
    @validator("max_line_length")
    def validate_line_length(cls, v, values):
        """Валидация длины строки для субтитров."""
        format_type = values.get("format")
        if format_type in [OutputFormat.SRT, OutputFormat.VTT] and v > 150:
            raise ValueError("Для субтитров максимальная длина строки не должна превышать 150 символов")
        return v