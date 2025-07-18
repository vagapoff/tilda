"""
Сервис транскрипции видео (MVP версия с заглушками).
"""

from typing import Dict, Any, Optional
import os
import asyncio
from datetime import datetime

from app.models.schemas import (
    TaskStatus, TranscriptionResult, TranscriptionSegment,
    VideoMetadata, Platform, OutputFormat
)
from app.services.task_manager import TaskManager
from app.core.config import settings


class TranscriptionService:
    """Сервис для транскрипции видео."""
    
    def __init__(self):
        """Инициализация сервиса транскрипции."""
        self.task_manager = TaskManager()
    
    async def process_file(
        self, 
        task_id: str, 
        file_path: str, 
        params: Dict[str, Any]
    ):
        """
        Обработка загруженного файла.
        
        Args:
            task_id: ID задачи
            file_path: Путь к файлу
            params: Параметры обработки
        """
        try:
            # Обновление статуса - начало обработки
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.PROCESSING, 
                progress=10.0,
                message="Начало обработки файла"
            )
            
            # Эмуляция обработки (для MVP)
            await asyncio.sleep(2)
            
            # Извлечение аудио
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.PROCESSING, 
                progress=30.0,
                message="Извлечение аудиодорожки"
            )
            
            await asyncio.sleep(3)
            
            # Транскрипция
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.TRANSCRIBING, 
                progress=50.0,
                message="Транскрипция аудио"
            )
            
            await asyncio.sleep(5)
            
            # Создание заглушки результата для MVP
            result = TranscriptionResult(
                text=f"Это тестовая транскрипция для файла {os.path.basename(file_path)}. "
                     f"В финальной версии здесь будет реальный текст из видео.",
                segments=[
                    TranscriptionSegment(
                        start=0.0,
                        end=5.0,
                        text="Это тестовая транскрипция",
                        confidence=0.95
                    ),
                    TranscriptionSegment(
                        start=5.0,
                        end=10.0,
                        text=f"для файла {os.path.basename(file_path)}",
                        confidence=0.92
                    )
                ],
                language="ru",
                confidence=0.93,
                processing_time=10.0
            )
            
            # Завершение
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.COMPLETED, 
                progress=100.0,
                message="Транскрипция завершена",
                result=result
            )
            
        except Exception as e:
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.FAILED, 
                progress=0.0,
                message="Ошибка при обработке файла",
                error=str(e)
            )
    
    async def process_url(
        self, 
        task_id: str, 
        url: str, 
        params: Dict[str, Any]
    ):
        """
        Обработка видео по URL.
        
        Args:
            task_id: ID задачи
            url: URL видео
            params: Параметры обработки
        """
        try:
            # Обновление статуса - начало скачивания
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.DOWNLOADING, 
                progress=5.0,
                message="Скачивание видео"
            )
            
            # Эмуляция скачивания
            await asyncio.sleep(3)
            
            # Создание заглушки метаданных
            metadata = VideoMetadata(
                title="Тестовое видео (MVP)",
                duration=120,  # 2 минуты
                thumbnail="https://example.com/thumb.jpg",
                description="Тестовое описание для MVP версии",
                platform=self._detect_platform(url),
                original_url=url
            )
            
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.PROCESSING, 
                progress=25.0,
                message="Видео скачано, начало обработки",
                video_metadata=metadata
            )
            
            # Эмуляция обработки
            await asyncio.sleep(4)
            
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.TRANSCRIBING, 
                progress=60.0,
                message="Транскрипция аудио"
            )
            
            await asyncio.sleep(6)
            
            # Создание заглушки результата
            result = TranscriptionResult(
                text=f"Это тестовая транскрипция для видео с {metadata.platform.value}. "
                     f"Название: {metadata.title}. В финальной версии здесь будет реальный текст.",
                segments=[
                    TranscriptionSegment(
                        start=0.0,
                        end=15.0,
                        text="Это тестовая транскрипция для видео",
                        confidence=0.94
                    ),
                    TranscriptionSegment(
                        start=15.0,
                        end=30.0,
                        text=f"с платформы {metadata.platform.value}",
                        confidence=0.91
                    )
                ],
                language="ru",
                confidence=0.92,
                processing_time=13.0
            )
            
            # Завершение
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.COMPLETED, 
                progress=100.0,
                message="Транскрипция завершена",
                result=result
            )
            
        except Exception as e:
            await self.task_manager.update_task_status(
                task_id, 
                TaskStatus.FAILED, 
                progress=0.0,
                message="Ошибка при обработке URL",
                error=str(e)
            )
    
    async def export_result(
        self,
        task_id: str,
        result: TranscriptionResult,
        format: OutputFormat
    ) -> str:
        """
        Экспорт результата в файл.
        
        Args:
            task_id: ID задачи
            result: Результат транскрипции
            format: Формат экспорта
        
        Returns:
            str: Путь к созданному файлу
        """
        # Создание директории для результатов
        results_dir = os.path.join(settings.TEMP_DIR, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        filename = f"{task_id}.{format.value}"
        file_path = os.path.join(results_dir, filename)
        
        if format == OutputFormat.TXT:
            content = result.text
        elif format == OutputFormat.SRT:
            content = self._create_srt(result.segments)
        elif format == OutputFormat.VTT:
            content = self._create_vtt(result.segments)
        elif format == OutputFormat.JSON:
            import json
            content = json.dumps(result.dict(), ensure_ascii=False, indent=2)
        elif format == OutputFormat.DOCX:
            # Заглушка для DOCX
            content = result.text
        else:
            content = result.text
        
        # Сохранение файла
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def _detect_platform(self, url: str) -> Platform:
        """Определение платформы по URL."""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return Platform.YOUTUBE
        elif 'instagram.com' in url_lower:
            return Platform.INSTAGRAM
        elif 'vk.com' in url_lower or 'vkontakte.ru' in url_lower:
            return Platform.VKONTAKTE
        elif 'tiktok.com' in url_lower:
            return Platform.TIKTOK
        else:
            return Platform.OTHER
    
    def _create_srt(self, segments: list) -> str:
        """Создание SRT субтитров."""
        srt_content = []
        
        for i, segment in enumerate(segments, 1):
            start_time = self._seconds_to_srt_time(segment.start)
            end_time = self._seconds_to_srt_time(segment.end)
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment.text)
            srt_content.append("")
        
        return "\n".join(srt_content)
    
    def _create_vtt(self, segments: list) -> str:
        """Создание VTT субтитров."""
        vtt_content = ["WEBVTT", ""]
        
        for segment in segments:
            start_time = self._seconds_to_vtt_time(segment.start)
            end_time = self._seconds_to_vtt_time(segment.end)
            
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(segment.text)
            vtt_content.append("")
        
        return "\n".join(vtt_content)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Конвертация секунд в формат времени SRT."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Конвертация секунд в формат времени VTT."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"