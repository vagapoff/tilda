"""
Эндпоинты для транскрипции видео.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import uuid
import os
from datetime import datetime

from app.models.schemas import (
    TaskResponse, TaskStatusResponse, URLTranscriptionRequest,
    TranscriptionRequest, ErrorResponse, TaskStatus, SourceType,
    Language, OutputFormat
)
from app.services.transcription_service import TranscriptionService
from app.services.task_manager import TaskManager
from app.core.config import settings

router = APIRouter()

# Сервисы
transcription_service = TranscriptionService()
task_manager = TaskManager()


@router.post("/", response_model=TaskResponse, summary="Загрузка файла для транскрипции")
async def upload_file_for_transcription(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Видеофайл для транскрипции"),
    language: Language = Form(Language.AUTO, description="Язык аудио"),
    output_format: OutputFormat = Form(OutputFormat.SRT, description="Формат вывода"),
    include_timestamps: bool = Form(True, description="Включать временные метки"),
    max_line_length: Optional[int] = Form(80, description="Максимальная длина строки"),
    max_subtitle_duration: Optional[int] = Form(5, description="Максимальная длительность субтитра")
):
    """
    Загрузка видеофайла для транскрипции.
    
    Поддерживаемые форматы: MP4, AVI, MOV, MKV, WMV, FLV, WebM
    Максимальный размер: 2 ГБ
    Максимальная длительность: 4 часа
    """
    try:
        # Валидация файла
        if not file.filename:
            raise HTTPException(status_code=400, detail="Файл не выбран")
        
        # Проверка расширения
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Неподдерживаемый формат файла. Поддерживаемые: {', '.join(allowed_extensions)}"
            )
        
        # Создание задачи
        task_id = str(uuid.uuid4())
        
        # Сохранение файла
        file_path = os.path.join(settings.UPLOAD_DIR, f"{task_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            
            # Проверка размера файла
            if len(content) > settings.MAX_FILE_SIZE * 1024 * 1024:  # МБ в байты
                os.remove(file_path)
                raise HTTPException(
                    status_code=413, 
                    detail=f"Файл слишком большой. Максимальный размер: {settings.MAX_FILE_SIZE} МБ"
                )
            
            buffer.write(content)
        
        # Создание задачи в менеджере
        task = await task_manager.create_task(
            task_id=task_id,
            source_type=SourceType.FILE,
            source_path=file_path,
            request_params={
                "language": language,
                "output_format": output_format,
                "include_timestamps": include_timestamps,
                "max_line_length": max_line_length,
                "max_subtitle_duration": max_subtitle_duration
            }
        )
        
        # Запуск обработки в фоне
        background_tasks.add_task(
            transcription_service.process_file,
            task_id, file_path, task.request_params
        )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")


@router.post("/url", response_model=TaskResponse, summary="Транскрипция видео по ссылке")
async def transcribe_from_url(
    background_tasks: BackgroundTasks,
    request: URLTranscriptionRequest
):
    """
    Транскрипция видео по ссылке.
    
    Поддерживаемые платформы:
    - YouTube (youtube.com, youtu.be)
    - Instagram (instagram.com)
    - ВКонтакте (vk.com)
    - TikTok (tiktok.com)
    
    Максимальная длительность: 2 часа
    """
    try:
        # Создание задачи
        task_id = str(uuid.uuid4())
        
        # Создание задачи в менеджере
        task = await task_manager.create_task(
            task_id=task_id,
            source_type=SourceType.URL,
            source_url=str(request.url),
            request_params=request.dict()
        )
        
        # Запуск обработки в фоне
        background_tasks.add_task(
            transcription_service.process_url,
            task_id, str(request.url), request.dict()
        )
        
        return task
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании задачи: {str(e)}")


@router.get("/{task_id}/status", response_model=TaskStatusResponse, summary="Статус задачи")
async def get_task_status(task_id: str):
    """Получение статуса задачи транскрипции."""
    try:
        task = await task_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        return TaskStatusResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            message=task.message,
            error=task.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении статуса: {str(e)}")


@router.get("/{task_id}/result", response_model=TaskResponse, summary="Результат транскрипции")
async def get_transcription_result(task_id: str):
    """Получение результата транскрипции."""
    try:
        task = await task_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Задача еще не завершена. Текущий статус: {task.status}"
            )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении результата: {str(e)}")


@router.get("/{task_id}/download", summary="Скачивание файла результата")
async def download_transcription_file(task_id: str, format: Optional[OutputFormat] = None):
    """Скачивание файла с результатом транскрипции."""
    try:
        task = await task_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Задача еще не завершена. Текущий статус: {task.status}"
            )
        
        # Определение формата
        export_format = format or task.request_params.get("output_format", OutputFormat.SRT)
        
        # Генерация файла
        file_path = await transcription_service.export_result(
            task_id, task.result, export_format
        )
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Файл результата не найден")
        
        # Определение типа контента
        content_types = {
            OutputFormat.TXT: "text/plain",
            OutputFormat.SRT: "application/x-subrip",
            OutputFormat.VTT: "text/vtt",
            OutputFormat.JSON: "application/json",
            OutputFormat.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        
        return FileResponse(
            file_path,
            media_type=content_types.get(export_format, "application/octet-stream"),
            filename=f"transcription_{task_id}.{export_format.value}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при скачивании файла: {str(e)}")


@router.delete("/{task_id}", summary="Удаление задачи")
async def delete_task(task_id: str):
    """Удаление задачи и связанных файлов."""
    try:
        success = await task_manager.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        return {"message": "Задача успешно удалена"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении задачи: {str(e)}")


@router.get("/", summary="Список задач пользователя")
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None
):
    """Получение списка задач пользователя."""
    try:
        tasks = await task_manager.list_tasks(skip=skip, limit=limit, status=status)
        return {
            "tasks": tasks,
            "total": len(tasks),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка задач: {str(e)}")