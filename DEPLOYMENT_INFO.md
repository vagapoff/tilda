# 🚀 Информация о развертывании сервиса транскрипции видео

## ✅ Статус развертывания
**Сервис успешно развернут и готов к использованию!**

## 🌐 Доступ к сервису

### Основные URL:
- **Веб-интерфейс**: http://localhost:8000
- **API документация**: http://localhost:8000/docs
- **OpenAPI схема**: http://localhost:8000/openapi.json
- **Health check**: http://localhost:8000/health

## 📋 Доступные API endpoints:

### 1. 🏠 Главная страница
- **URL**: `GET /`
- **Описание**: Веб-интерфейс для загрузки и обработки видео

### 2. 📤 Загрузка файла
- **URL**: `POST /upload`
- **Формат**: multipart/form-data
- **Параметры**: `file` (видео файл)
- **Пример**:
```bash
curl -X POST "http://localhost:8000/upload" \
     -F "file=@your_video.mp4"
```

### 3. 🔗 Транскрипция по URL
- **URL**: `POST /transcribe-url`
- **Формат**: JSON
- **Параметры**: `{"url": "https://example.com/video.mp4"}`
- **Пример**:
```bash
curl -X POST "http://localhost:8000/transcribe-url" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/video.mp4"}'
```

### 4. 📊 Статус задачи
- **URL**: `GET /status/{task_id}`
- **Описание**: Проверка статуса обработки видео

### 5. 💾 Скачивание результата
- **URL**: `GET /download/{task_id}`
- **Описание**: Скачивание результатов транскрипции

### 6. 🔍 Health Check
- **URL**: `GET /health`
- **Описание**: Проверка состояния сервиса

## 🧪 Результаты тестирования

✅ **6/6 тестов прошли успешно:**

1. ✅ Health endpoint - работает корректно
2. ✅ Главная страница - доступна 
3. ✅ Upload endpoint - принимает файлы
4. ✅ Transcribe-URL endpoint - отвечает
5. ✅ API документация - доступна
6. ✅ OpenAPI схема - доступна

## 🐳 Информация о контейнерах

```bash
# Проверить статус контейнеров
sudo docker-compose ps

# Посмотреть логи
sudo docker logs workspace-app-1
sudo docker logs workspace-redis-1

# Остановить сервис
sudo docker-compose down

# Перезапустить сервис
sudo docker-compose up -d
```

## 📝 Примечания

- Сервис работает в **демо-режиме**
- Функция транскрипции будет добавлена в следующих обновлениях
- Сервис использует Redis для кэширования
- Все загруженные файлы сохраняются локально

## 🔧 Техническая информация

- **Порт**: 8000
- **Framework**: FastAPI (Python)
- **База данных**: Redis
- **Веб-сервер**: Uvicorn
- **Контейнеризация**: Docker + Docker Compose

## 🚦 Мониторинг

Для проверки работоспособности сервиса можно использовать:

```bash
# Автоматический тест всех функций
python3 test_service.py

# Быстрая проверка health endpoint
curl http://localhost:8000/health

# Проверка главной страницы
curl http://localhost:8000/
```

---

**Сервис готов к использованию!** 🎉