"""
Загрузчик видео (MVP версия с заглушками).
"""

from typing import Optional
import asyncio

from app.models.schemas import VideoMetadata, Platform


class VideoDownloader:
    """Загрузчик видео с различных платформ."""
    
    def __init__(self):
        """Инициализация загрузчика."""
        pass
    
    async def get_video_info(self, url: str) -> VideoMetadata:
        """
        Получение информации о видео без скачивания.
        
        Args:
            url: URL видео
        
        Returns:
            VideoMetadata: Метаданные видео
        """
        # Эмуляция запроса к API (для MVP)
        await asyncio.sleep(1)
        
        platform = self._detect_platform(url)
        
        # Заглушки метаданных в зависимости от платформы
        if platform == Platform.YOUTUBE:
            return VideoMetadata(
                title="Тестовое YouTube видео (MVP)",
                duration=180,  # 3 минуты
                thumbnail="https://i.ytimg.com/vi/test/maxresdefault.jpg",
                description="Это тестовое описание YouTube видео для MVP версии",
                platform=platform,
                original_url=url
            )
        
        elif platform == Platform.INSTAGRAM:
            return VideoMetadata(
                title="Instagram Reel (MVP)",
                duration=30,  # 30 секунд
                thumbnail="https://scontent.cdninstagram.com/test.jpg",
                description="Тестовое Instagram видео",
                platform=platform,
                original_url=url
            )
        
        elif platform == Platform.VKONTAKTE:
            return VideoMetadata(
                title="Видео ВКонтакте (MVP)",
                duration=120,  # 2 минуты
                thumbnail="https://sun9-74.userapi.com/test.jpg",
                description="Тестовое видео из ВКонтакте",
                platform=platform,
                original_url=url
            )
        
        elif platform == Platform.TIKTOK:
            return VideoMetadata(
                title="TikTok видео (MVP)",
                duration=15,  # 15 секунд
                thumbnail="https://p16-sign-sg.tiktokcdn.com/test.webp",
                description="Тестовое TikTok видео",
                platform=platform,
                original_url=url
            )
        
        else:
            return VideoMetadata(
                title="Неизвестное видео (MVP)",
                duration=60,
                thumbnail=None,
                description="Тестовое видео с неизвестной платформы",
                platform=Platform.OTHER,
                original_url=url
            )
    
    async def download_video(self, url: str, output_path: str) -> str:
        """
        Скачивание видео по URL.
        
        Args:
            url: URL видео
            output_path: Путь для сохранения
        
        Returns:
            str: Путь к скачанному файлу
        """
        # Эмуляция скачивания для MVP
        await asyncio.sleep(3)
        
        # В реальной версии здесь будет yt-dlp или другой загрузчик
        print(f"[MVP] Эмуляция скачивания видео с {url} в {output_path}")
        
        # Создание пустого файла для тестирования
        with open(output_path, 'w') as f:
            f.write("Mock video file for MVP testing")
        
        return output_path
    
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