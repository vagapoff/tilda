"""
Валидатор URL (MVP версия с заглушками).
"""

from typing import Optional
from dataclasses import dataclass

from app.models.schemas import Platform


@dataclass
class ValidationResult:
    """Результат валидации URL."""
    is_valid: bool
    platform: Optional[Platform] = None
    reason: Optional[str] = None


class URLValidator:
    """Валидатор URL для видеоплатформ."""
    
    def __init__(self):
        """Инициализация валидатора."""
        self.supported_domains = {
            Platform.YOUTUBE: ["youtube.com", "youtu.be", "m.youtube.com"],
            Platform.INSTAGRAM: ["instagram.com", "www.instagram.com"],
            Platform.VKONTAKTE: ["vk.com", "vkontakte.ru", "m.vk.com"],
            Platform.TIKTOK: ["tiktok.com", "www.tiktok.com", "m.tiktok.com"]
        }
    
    async def validate_url(self, url: str) -> ValidationResult:
        """
        Валидация URL видео.
        
        Args:
            url: URL для проверки
        
        Returns:
            ValidationResult: Результат валидации
        """
        url_lower = url.lower().strip()
        
        # Базовая проверка URL
        if not url_lower.startswith(('http://', 'https://')):
            return ValidationResult(
                is_valid=False,
                reason="URL должен начинаться с http:// или https://"
            )
        
        # Определение платформы
        detected_platform = None
        for platform, domains in self.supported_domains.items():
            if any(domain in url_lower for domain in domains):
                detected_platform = platform
                break
        
        if not detected_platform:
            return ValidationResult(
                is_valid=False,
                reason="Неподдерживаемая платформа. Поддерживаемые: YouTube, Instagram, ВКонтакте, TikTok"
            )
        
        # Специфическая валидация для каждой платформы (заглушки для MVP)
        if detected_platform == Platform.YOUTUBE:
            if not self._validate_youtube_url(url_lower):
                return ValidationResult(
                    is_valid=False,
                    platform=detected_platform,
                    reason="Некорректный формат YouTube URL"
                )
        
        elif detected_platform == Platform.INSTAGRAM:
            if not self._validate_instagram_url(url_lower):
                return ValidationResult(
                    is_valid=False,
                    platform=detected_platform,
                    reason="Некорректный формат Instagram URL"
                )
        
        elif detected_platform == Platform.VKONTAKTE:
            if not self._validate_vk_url(url_lower):
                return ValidationResult(
                    is_valid=False,
                    platform=detected_platform,
                    reason="Некорректный формат ВКонтакте URL"
                )
        
        elif detected_platform == Platform.TIKTOK:
            if not self._validate_tiktok_url(url_lower):
                return ValidationResult(
                    is_valid=False,
                    platform=detected_platform,
                    reason="Некорректный формат TikTok URL"
                )
        
        return ValidationResult(
            is_valid=True,
            platform=detected_platform
        )
    
    def _validate_youtube_url(self, url: str) -> bool:
        """Валидация YouTube URL (заглушка)."""
        # Базовая проверка на наличие video ID
        return (
            'watch?v=' in url or 
            'youtu.be/' in url or 
            'embed/' in url or
            'shorts/' in url
        )
    
    def _validate_instagram_url(self, url: str) -> bool:
        """Валидация Instagram URL (заглушка)."""
        return (
            '/p/' in url or 
            '/reel/' in url or 
            '/tv/' in url or
            '/stories/' in url
        )
    
    def _validate_vk_url(self, url: str) -> bool:
        """Валидация ВКонтакте URL (заглушка)."""
        return 'video' in url and ('video-' in url or 'video_ext.php' in url)
    
    def _validate_tiktok_url(self, url: str) -> bool:
        """Валидация TikTok URL (заглушка)."""
        return '/video/' in url or '@' in url