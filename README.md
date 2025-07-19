# 🎬 Video Transcription Agent

Веб-приложение для автоматической транскрипции видео и аудио файлов с использованием искусственного интеллекта.

## 🚀 Особенности

- **Загрузка файлов**: Поддержка видео и аудио файлов различных форматов
- **URL-транскрипция**: Обработка видео по ссылкам (YouTube, Instagram, VK и др.)
- **Современный UI**: Красивый и интуитивно понятный веб-интерфейс
- **Drag & Drop**: Удобная загрузка файлов перетаскиванием
- **REST API**: Полноценное API для интеграции с другими сервисами

## 📋 Требования

- Python 3.11+
- FFmpeg (для обработки видео)
- Виртуальное окружение (рекомендуется)

## 🛠 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd video-transcription-agent
```

### 2. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
# venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Запуск приложения
```bash
python app/main.py
```

### 5. Быстрый запуск с Docker (альтернатива)
```bash
chmod +x run.sh
./run.sh
```

## 🌐 Использование

1. Откройте браузер и перейдите по адресу: `http://localhost:8000`
2. Выберите способ загрузки:
   - **Загрузить файл**: Перетащите файл или нажмите для выбора
   - **Ссылка на видео**: Введите URL видео

3. Дождитесь завершения обработки
4. Скачайте результат в нужном формате

## 📡 API Endpoints

### Основные эндпоинты:

- `GET /` - Главная страница
- `POST /upload` - Загрузка файла
- `POST /transcribe-url` - Транскрипция по URL
- `GET /status/{task_id}` - Статус задачи
- `GET /download/{task_id}` - Скачивание результата
- `GET /health` - Проверка состояния сервиса

### Пример использования API:

```bash
# Загрузка файла
curl -X POST -F "file=@video.mp4" http://localhost:8000/upload

# Транскрипция по URL
curl -X POST -F "url=https://youtube.com/watch?v=..." http://localhost:8000/transcribe-url

# Проверка статуса
curl http://localhost:8000/status/task-id

# Скачивание результата
curl http://localhost:8000/download/task-id -o result.json
```

## 📁 Структура проекта

```
video-transcription-agent/
├── app/
│   └── main.py              # Основное приложение FastAPI
├── templates/
│   └── index.html           # HTML шаблон
├── static/
│   └── style.css           # CSS стили
├── uploads/                 # Загруженные файлы
├── outputs/                 # Результаты транскрипции
├── requirements.txt         # Python зависимости
├── Dockerfile              # Docker конфигурация
├── docker-compose.yml      # Docker Compose конфигурация
├── run.sh                  # Скрипт быстрого запуска
└── README.md               # Документация
```

## 🔧 Конфигурация

### Переменные окружения:
- `HOST` - хост сервера (по умолчанию: 0.0.0.0)
- `PORT` - порт сервера (по умолчанию: 8000)
- `DEBUG` - режим отладки (по умолчанию: False)

## 🎯 Текущее состояние (MVP)

Это базовая демо-версия проекта, включающая:
- ✅ Веб-интерфейс для загрузки файлов
- ✅ REST API для основных операций
- ✅ Обработка файлов и URL
- ✅ Система статусов задач
- ✅ Скачивание результатов

### Планируемые функции:
- 🔄 Интеграция с Whisper AI для реальной транскрипции
- 🔄 Поддержка различных языков
- 🔄 Экспорт в SRT, VTT, TXT форматы
- 🔄 Обработка длинных видео
- 🔄 Пользовательские аккаунты
- 🔄 История транскрипций

## 🛠 Разработка

### Добавление новых функций:
1. Форкните репозиторий
2. Создайте feature branch: `git checkout -b feature-name`
3. Внесите изменения и добавьте тесты
4. Отправьте pull request

### Запуск в режиме разработки:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📄 Лицензия

MIT License - подробности в файле LICENSE

## 🤝 Поддержка

Если у вас есть вопросы или предложения:
- Создайте Issue в репозитории
- Отправьте Pull Request с улучшениями

## 🔗 Полезные ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

---

**Статус проекта:** 🚧 В разработке (MVP готов)

Создано согласно техническому заданию `video_transcription_agent_requirements.md`
