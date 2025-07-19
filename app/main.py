from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiofiles
import os
import uuid
import json
from datetime import datetime
from pathlib import Path
import asyncio
from typing import Optional
import tempfile
import shutil
import requests

app = FastAPI(title="Video Transcription Agent", version="1.0.0")

# Создаем директории
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Загрузка файла для транскрипции"""
    try:
        # Проверяем тип файла
        if not file.content_type or not file.content_type.startswith(('video/', 'audio/')):
            raise HTTPException(status_code=400, detail="Поддерживаются только видео и аудио файлы")
        
        # Генерируем уникальное имя файла
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{file_id}{file_extension}"
        file_path = os.path.join("uploads", safe_filename)
        
        # Сохраняем файл
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Возвращаем информацию о файле
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "status": "uploaded",
            "message": "Файл успешно загружен. Функция транскрипции будет добавлена в следующей версии."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")

@app.post("/transcribe-url")
async def transcribe_url(url: str = Form(...)):
    """Транскрипция видео по URL"""
    try:
        # Базовая проверка URL
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Некорректный URL")
        
        # Генерируем ID для задачи
        task_id = str(uuid.uuid4())
        
        return {
            "task_id": task_id,
            "url": url,
            "status": "pending",
            "message": "URL получен. Функция скачивания и транскрипции будет добавлена в следующей версии."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке URL: {str(e)}")

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Получение статуса задачи"""
    return {
        "task_id": task_id,
        "status": "completed",
        "progress": 100,
        "message": "Это демо-версия. Функция транскрипции будет добавлена позже."
    }

@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """Скачивание результата транскрипции"""
    # Создаем демо-результат
    demo_result = {
        "task_id": task_id,
        "transcription": "Это демо-транскрипция. Настоящая функция транскрипции будет добавлена в следующей версии.",
        "timestamp": datetime.now().isoformat(),
        "language": "ru",
        "confidence": 0.95
    }
    
    # Сохраняем во временный файл
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(demo_result, temp_file, ensure_ascii=False, indent=2)
    temp_file.close()
    
    return FileResponse(
        temp_file.name,
        media_type='application/json',
        filename=f"transcription_{task_id}.json"
    )

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)