import base64
import requests
from django.conf import settings

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле для картинки"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='rec.' + ext)
        return super().to_internal_value(data)


def fetch_rock_music_news():
    """
    Получает новости о рок-музыке с NewsAPI.org на русском языке.
    """
    base_url = "https://newsapi.org/v2/everything"
    params = {
        "q": "рок-музыка OR рок-группа OR альбом рок",
        "apiKey": settings.NEWS_API_KEY,
        "language": "ru",  # Устанавливаем русский язык
        "sortBy": "publishedAt",  # Сортировка по дате публикации
        "pageSize": 20,  # Количество новостей, которое мы хотим получить
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            raise Exception(f"Ошибка от NewsAPI: {data.get('message')}")
    else:
        raise Exception(f"HTTP Error: {response.status_code}")
