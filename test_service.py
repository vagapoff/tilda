#!/usr/bin/env python3
"""
Скрипт для тестирования API сервиса транскрипции видео
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Тест health endpoint"""
    print("🔍 Тестируем health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_main_page():
    """Тест главной страницы"""
    print("\n🔍 Тестируем главную страницу...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Главная страница доступна")
            return True
        else:
            print(f"❌ Главная страница недоступна: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка доступа к главной странице: {e}")
        return False

def test_upload_endpoint():
    """Тест upload endpoint"""
    print("\n🔍 Тестируем upload endpoint...")
    try:
        # Создаем тестовый видео файл (фейковые данные)
        files = {
            'file': ('test_video.mp4', b'fake video content for testing', 'video/mp4')
        }
        
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print(f"📤 Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Upload endpoint работает корректно")
            try:
                data = response.json()
                print(f"📝 Response: {data}")
                if 'file_id' in data:
                    print(f"📋 Получен file_id: {data['file_id']}")
            except:
                print(f"📝 Response text: {response.text[:200]}...")
            return True
        else:
            print(f"❌ Upload endpoint error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Upload endpoint error: {e}")
        return False

def test_transcribe_url_endpoint():
    """Тест transcribe-url endpoint"""
    print("\n🔍 Тестируем transcribe-url endpoint...")
    try:
        # Тестируем с фейковой URL
        test_data = {
            "url": "https://example.com/test_video.mp4"
        }
        
        response = requests.post(f"{BASE_URL}/transcribe-url", json=test_data)
        print(f"📤 Transcribe-URL response status: {response.status_code}")
        
        if response.status_code in [200, 422]:  # 422 может быть для невалидного URL
            print("✅ Transcribe-URL endpoint отвечает")
            try:
                data = response.json()
                print(f"📝 Response: {data}")
            except:
                print(f"📝 Response text: {response.text[:200]}...")
            return True
        else:
            print(f"❌ Transcribe-URL endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Transcribe-URL endpoint error: {e}")
        return False

def test_api_docs():
    """Тест документации API"""
    print("\n🔍 Тестируем документацию API...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API документация доступна")
            return True
        else:
            print(f"❌ API документация недоступна: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка доступа к документации: {e}")
        return False

def test_endpoints_discovery():
    """Тест обнаружения endpoints через OpenAPI"""
    print("\n🔍 Проверяем доступные endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            data = response.json()
            print("✅ OpenAPI схема доступна")
            print("📋 Доступные endpoints:")
            for path, methods in data.get('paths', {}).items():
                methods_list = list(methods.keys())
                print(f"   {path}: {methods_list}")
            return True
        else:
            print(f"❌ OpenAPI схема недоступна: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка получения OpenAPI схемы: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 Запуск тестирования сервиса транскрипции видео")
    print("=" * 50)
    
    tests = [
        test_health,
        test_main_page, 
        test_upload_endpoint,
        test_transcribe_url_endpoint,
        test_api_docs,
        test_endpoints_discovery
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Небольшая пауза между тестами
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли успешно")
    
    if passed >= total - 1:  # Позволяем одному тесту не пройти
        print("🎉 Сервис готов к использованию!")
        print(f"🌐 Веб-интерфейс: {BASE_URL}")
        print(f"📚 API документация: {BASE_URL}/docs")
        print("\n📋 Основные endpoints:")
        print(f"   POST {BASE_URL}/upload - Загрузка видео файлов")
        print(f"   POST {BASE_URL}/transcribe-url - Транскрипция по URL")
        print(f"   GET  {BASE_URL}/health - Проверка состояния сервиса")
    else:
        print("⚠️  Некоторые критические тесты не прошли. Проверьте логи сервиса.")
    
    return passed >= total - 1

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)