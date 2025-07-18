"""
Главный модуль приложения агента транскрипции видео.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация при запуске
    print("🚀 Запуск агента транскрипции видео...")
    print(f"📊 Режим: {settings.ENVIRONMENT}")
    yield
    # Очистка при завершении
    print("🔄 Завершение работы агента транскрипции...")


# Создание FastAPI приложения
app = FastAPI(
    title="Агент по транскрипции видео",
    description="Автоматизированный сервис для извлечения текста из видеофайлов и видео по ссылкам",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API роутеры
app.include_router(api_router, prefix="/api/v1")

# Статические файлы (для веб-интерфейса)
if settings.SERVE_STATIC:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с веб-интерфейсом."""
    try:
        # Путь к HTML файлу
        html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
        
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Fallback на JSON ответ если HTML не найден
            return HTMLResponse(content="""
                <html>
                    <head><title>Агент транскрипции видео</title></head>
                    <body>
                        <h1>🎬 Агент по транскрипции видео</h1>
                        <p>Веб-интерфейс недоступен</p>
                        <p><a href="/docs">API документация</a></p>
                    </body>
                </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"""
            <html>
                <head><title>Ошибка</title></head>
                <body>
                    <h1>Ошибка загрузки интерфейса</h1>
                    <p>{str(e)}</p>
                    <p><a href="/docs">API документация</a></p>
                </body>
            </html>
        """)


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {
        "status": "healthy",
        "service": "video-transcription-agent",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        workers=1 if settings.ENVIRONMENT == "development" else settings.WORKERS,
    )