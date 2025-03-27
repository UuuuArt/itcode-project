from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from reviews.models import Band, Review, Title
from users.models import User


def get_token_for_user(client, username, password):
    """Получает JWT-токен для пользователя."""
    response = client.post(reverse('api:jwt-create'), data={'username': username, 'password': password})
    return response.data.get('access', None)


class ReviewViewSetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='a@mail.ru', password='password')

        cls.band = Band.objects.create(name="Band test")

        cls.title = Title.objects.create(name="Test Title", year=2024)
        cls.title.band.set([cls.band])

        cls.review_data = {
            "text": "Great review!",
            "score": 5,
            "title": cls.title.id,
            "author": cls.user.id
        }

    def setUp(self):
        self.user_token = get_token_for_user(self.client, self.user.username, 'password')
        if not self.user_token:
            self.fail("Не удалось получить JWT токен")

    def test_create_review(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('api:reviews-list', kwargs={'title_id': self.title.id})
        response = self.client.post(url, self.review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_review_without_auth(self):
        url = reverse('api:reviews-list', kwargs={'title_id': self.title.id})
        response = self.client.post(url, self.review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_reviews(self):
        Review.objects.create(text="Nice review", score=4, title=self.title, author=self.user)
        url = reverse('api:reviews-list', kwargs={'title_id': self.title.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.filter(title=self.title).count(), 1)


class ProfileViewSetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='a@mail.ru', password='password')
        cls.profile_data = {"bio": "Test bio", "birth_date": "1990-01-01"}

    def setUp(self):
        self.user_token = get_token_for_user(self.client, self.user.username, 'password')
        if not self.user_token:
            self.fail("Не удалось получить JWT токен")

    def test_get_profile(self):
        url = reverse('api:profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('api:profile-detail', kwargs={'user__username': self.user.username})
        response = self.client.patch(url, self.profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], "Test bio")

    def test_update_profile_without_auth(self):
        url = reverse('api:profile-detail', kwargs={'user__username': self.user.username})
        response = self.client.patch(url, self.profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HomePageViewTests(APITestCase):

    def test_homepage(self):
        url = reverse('api:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("popular_bands", response.data)
        self.assertIn("latest_reviews", response.data)
        self.assertIn("latest_titles", response.data)
