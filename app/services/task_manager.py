"""
Менеджер задач для управления состоянием транскрипции.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.models.schemas import (
    TaskResponse, TaskStatus, SourceType, VideoMetadata, 
    TranscriptionResult
)
from app.core.config import settings


class TaskManager:
    """Менеджер для управления задачами транскрипции."""
    
    def __init__(self):
        """Инициализация менеджера задач."""
        self._tasks: Dict[str, TaskResponse] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Создание директорий для хранения результатов
        os.makedirs(os.path.join(settings.TEMP_DIR, "tasks"), exist_ok=True)
    
    async def create_task(
        self, 
        task_id: str, 
        source_type: SourceType,
        source_path: Optional[str] = None,
        source_url: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None
    ) -> TaskResponse:
        """
        Создание новой задачи транскрипции.
        
        Args:
            task_id: Уникальный ID задачи
            source_type: Тип источника (файл или URL)
            source_path: Путь к файлу (для файлов)
            source_url: URL источника (для ссылок)
            request_params: Параметры запроса
        
        Returns:
            TaskResponse: Объект задачи
        """
        now = datetime.utcnow()
        
        task = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            source_type=source_type,
            created_at=now,
            updated_at=now,
            progress=0.0,
            message="Задача создана, ожидание обработки",
            request_params=request_params or {}
        )
        
        # Добавление источника
        if source_type == SourceType.FILE and source_path:
            task.request_params["source_path"] = source_path
        elif source_type == SourceType.URL and source_url:
            task.request_params["source_url"] = source_url
        
        # Сохранение в памяти
        self._tasks[task_id] = task
        
        # Сохранение на диск
        await self._save_task_to_disk(task)
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """
        Получение задачи по ID.
        
        Args:
            task_id: ID задачи
        
        Returns:
            TaskResponse или None если задача не найдена
        """
        # Сначала проверяем в памяти
        if task_id in self._tasks:
            return self._tasks[task_id]
        
        # Если нет в памяти, загружаем с диска
        task = await self._load_task_from_disk(task_id)
        if task:
            self._tasks[task_id] = task
        
        return task
    
    async def update_task_status(
        self, 
        task_id: str, 
        status: TaskStatus,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        video_metadata: Optional[VideoMetadata] = None,
        result: Optional[TranscriptionResult] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Обновление статуса задачи.
        
        Args:
            task_id: ID задачи
            status: Новый статус
            progress: Прогресс (0-100)
            message: Сообщение о статусе
            video_metadata: Метаданные видео
            result: Результат транскрипции
            error: Ошибка (если есть)
        
        Returns:
            bool: True если задача обновлена успешно
        """
        task = await self.get_task(task_id)
        if not task:
            return False
        
        # Обновление полей
        task.status = status
        task.updated_at = datetime.utcnow()
        
        if progress is not None:
            task.progress = max(0.0, min(100.0, progress))
        
        if message is not None:
            task.message = message
        
        if video_metadata is not None:
            task.video_metadata = video_metadata
        
        if result is not None:
            task.result = result
        
        if error is not None:
            task.error = error
        
        # Сохранение обновлений
        self._tasks[task_id] = task
        await self._save_task_to_disk(task)
        
        return True
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Удаление задачи и связанных файлов.
        
        Args:
            task_id: ID задачи
        
        Returns:
            bool: True если задача удалена успешно
        """
        task = await self.get_task(task_id)
        if not task:
            return False
        
        # Удаление из памяти
        if task_id in self._tasks:
            del self._tasks[task_id]
        
        # Удаление файлов
        await self._cleanup_task_files(task)
        
        # Удаление файла задачи с диска
        task_file = os.path.join(settings.TEMP_DIR, "tasks", f"{task_id}.json")
        try:
            if os.path.exists(task_file):
                os.remove(task_file)
        except Exception as e:
            print(f"Ошибка при удалении файла задачи {task_id}: {e}")
        
        return True
    
    async def list_tasks(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[TaskStatus] = None
    ) -> List[TaskResponse]:
        """
        Получение списка задач.
        
        Args:
            skip: Количество задач для пропуска
            limit: Максимальное количество задач
            status: Фильтр по статусу
        
        Returns:
            List[TaskResponse]: Список задач
        """
        # Загрузка всех задач с диска (если еще не в памяти)
        await self._load_all_tasks_from_disk()
        
        # Фильтрация и сортировка
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        # Сортировка по времени создания (новые сначала)
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        # Пагинация
        return tasks[skip:skip + limit]
    
    async def cleanup_expired_tasks(self, max_age_hours: int = 24):
        """
        Очистка устаревших задач.
        
        Args:
            max_age_hours: Максимальный возраст задач в часах
        """
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        expired_tasks = []
        
        for task_id, task in self._tasks.items():
            if task.created_at.timestamp() < cutoff_time:
                expired_tasks.append(task_id)
        
        # Удаление устаревших задач
        for task_id in expired_tasks:
            await self.delete_task(task_id)
        
        print(f"Удалено {len(expired_tasks)} устаревших задач")
    
    async def _save_task_to_disk(self, task: TaskResponse):
        """Сохранение задачи на диск."""
        task_file = os.path.join(settings.TEMP_DIR, "tasks", f"{task.task_id}.json")
        
        try:
            task_data = task.dict()
            # Конвертируем datetime в строки для JSON
            task_data["created_at"] = task.created_at.isoformat()
            task_data["updated_at"] = task.updated_at.isoformat()
            
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка при сохранении задачи {task.task_id}: {e}")
    
    async def _load_task_from_disk(self, task_id: str) -> Optional[TaskResponse]:
        """Загрузка задачи с диска."""
        task_file = os.path.join(settings.TEMP_DIR, "tasks", f"{task_id}.json")
        
        if not os.path.exists(task_file):
            return None
        
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            # Конвертируем строки обратно в datetime
            task_data["created_at"] = datetime.fromisoformat(task_data["created_at"])
            task_data["updated_at"] = datetime.fromisoformat(task_data["updated_at"])
            
            return TaskResponse(**task_data)
            
        except Exception as e:
            print(f"Ошибка при загрузке задачи {task_id}: {e}")
            return None
    
    async def _load_all_tasks_from_disk(self):
        """Загрузка всех задач с диска."""
        tasks_dir = os.path.join(settings.TEMP_DIR, "tasks")
        
        if not os.path.exists(tasks_dir):
            return
        
        try:
            for filename in os.listdir(tasks_dir):
                if filename.endswith('.json'):
                    task_id = filename[:-5]  # Убираем .json
                    
                    # Загружаем только если еще нет в памяти
                    if task_id not in self._tasks:
                        task = await self._load_task_from_disk(task_id)
                        if task:
                            self._tasks[task_id] = task
                            
        except Exception as e:
            print(f"Ошибка при загрузке задач с диска: {e}")
    
    async def _cleanup_task_files(self, task: TaskResponse):
        """Очистка файлов связанных с задачей."""
        cleanup_paths = []
        
        # Исходный файл
        source_path = task.request_params.get("source_path")
        if source_path and os.path.exists(source_path):
            cleanup_paths.append(source_path)
        
        # Временные файлы для URL
        temp_video_path = os.path.join(settings.TEMP_DIR, f"{task.task_id}_video")
        temp_audio_path = os.path.join(settings.TEMP_DIR, f"{task.task_id}_audio")
        
        for pattern in [temp_video_path, temp_audio_path]:
            # Поиск файлов с различными расширениями
            for ext in ['.mp4', '.avi', '.mov', '.wav', '.mp3', '.m4a']:
                file_path = pattern + ext
                if os.path.exists(file_path):
                    cleanup_paths.append(file_path)
        
        # Файлы результатов
        results_dir = os.path.join(settings.TEMP_DIR, "results")
        if os.path.exists(results_dir):
            for filename in os.listdir(results_dir):
                if filename.startswith(task.task_id):
                    cleanup_paths.append(os.path.join(results_dir, filename))
        
        # Удаление файлов
        for file_path in cleanup_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Удален файл: {file_path}")
            except Exception as e:
                print(f"Ошибка при удалении файла {file_path}: {e}")
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Получение статистики задач."""
        total_tasks = len(self._tasks)
        status_counts = {}
        
        for task in self._tasks.values():
            status = task.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "status_distribution": status_counts,
            "memory_usage": len(self._tasks)
        }