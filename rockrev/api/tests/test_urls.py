from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from reviews.models import Band, Title, SubGenre


class APITests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователей
        cls.user = User.objects.create_user(username='user', password='password')
        # Создаем объекты, которые используются в тестах
        cls.band = Band.objects.create(name='Test Band', slug='band-slug')
        cls.subgenre = SubGenre.objects.create(name='Rock', slug='rock')
        cls.title = Title.objects.create(name='Test Title', year=2020)

    # Список URL для тестирования
    urls_to_test = [
        ("home", "GET"),
        ("bands-list", "GET"),
        ("subgenres-list", "GET"),
        ("titles-list", "GET"),
        ("reviews-list", "GET"),
        ("profile-list", "GET"),
        ("music-news", "GET"),
        ("follows-list", "GET"),
    ]

    def test_api_urls(self):
        for url_name, method in self.urls_to_test:
            if url_name == "reviews-list":
                url = reverse(f'api:{url_name}', args=[self.title.id])
            else:
                url = reverse(f'api:{url_name}')

            if method == "GET":
                response = self.client.get(url)

            if url_name == "follows-list":
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            else:
                self.assertEqual(response.status_code, status.HTTP_200_OK, f"Failed on {url_name}")
