#!/bin/bash

echo "🎬 Video Transcription Agent - Запуск приложения..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose."
    exit 1
fi

# Создаем необходимые директории
mkdir -p uploads outputs static

echo "📦 Сборка и запуск контейнеров..."

# Останавливаем существующие контейнеры
docker-compose down

# Собираем и запускаем
docker-compose up --build -d

echo "⏳ Ожидание запуска служб..."
sleep 10

# Проверяем статус
if docker-compose ps | grep -q "Up"; then
    echo "✅ Приложение успешно запущено!"
    echo "🌐 Откройте в браузере: http://localhost:8000"
    echo ""
    echo "📊 Для просмотра логов: docker-compose logs -f"
    echo "🛑 Для остановки: docker-compose down"
else
    echo "❌ Ошибка при запуске приложения"
    echo "📋 Просмотрите логи: docker-compose logs"
fi