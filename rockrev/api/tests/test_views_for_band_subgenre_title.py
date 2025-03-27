from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from reviews.models import Band, Title, SubGenre


def get_token_for_user(client, username, password):
    """Получает JWT-токен для пользователя."""
    response = client.post(reverse('api:jwt-create'), data={'username': username, 'password': password})
    return response.data['access']


class BandSlugTitlePermissionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(username='admin', email='a@mail.ru', password='admin')
        cls.regular_user = User.objects.create_user(username='user', password='password')
        cls.band = Band.objects.create(name="Test Band")
        cls.subgenre = SubGenre.objects.create(name="Test Subgenre")
        cls.title = Title.objects.create(name="Test Title", year=2024)
        cls.title.band.set([cls.band])
        cls.title.subgenre.set([cls.subgenre])

    def setUp(self):
        """Получаем JWT токены перед каждым тестом."""
        self.admin_token = get_token_for_user(self.client, 'admin', 'admin')
        self.user_token = get_token_for_user(self.client, 'user', 'password')

    def check_list_permission(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def check_create_permission(self, url, data):
        data = {
            "name": "New Title",
            "year": 2025,
            "band": [{"name": "Test Band"}],
            "subgenre": [{"name": "Test Subgenre"}]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def check_update_permission(self, url, data):
        data = {
            "name": "New Title",
            "year": 2025,
            "band": [{"name": "Test Band"}],
            "subgenre": [{"name": "Test Subgenre"}]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def check_delete_permission(self, url):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions(self):
        test_cases = [
            {'model': 'bands', 'instance': self.band, 'data': {'name': 'New Band', 'slug': 'new-band'}},
            {'model': 'subgenres', 'instance': self.subgenre,
             'data': {'name': 'New subgenre', 'slug': 'new-subgenre'}},
            {'model': 'titles', 'instance': self.title, 'data': {'name': 'New Title', 'year': 2025}},
        ]

        for case in test_cases:
            if case['model'] == 'bands' or case['model'] == 'subgenres':
                detail_url = reverse(f'api:{case["model"]}-detail', args=[case['instance'].slug])
            else:
                detail_url = reverse(f'api:{case["model"]}-detail', args=[case['instance'].pk])

            list_url = reverse(f'api:{case["model"]}-list')

            self.check_list_permission(list_url)
            self.check_create_permission(list_url, case['data'])
            self.check_update_permission(detail_url, case['data'])
            self.check_delete_permission(detail_url)
