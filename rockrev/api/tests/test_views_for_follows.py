from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from reviews.models import Band, FollowBand
from users.models import User


def get_token_for_user(client, username, password):
    """Получает JWT-токен для пользователя."""
    response = client.post(reverse('api:jwt-create'), data={'username': username, 'password': password})
    return response.data.get('access', None)


class FollowViewSetTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user', password='password')
        cls.band = Band.objects.create(name="Test Band", slug="test-band")

    def setUp(self):
        self.user_token = get_token_for_user(self.client, self.user.username, 'password')
        if not self.user_token:
            self.fail("Не удалось получить JWT токен")

    def test_follow_band(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('api:follow-list', args=[self.band.slug])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FollowBand.objects.filter(user=self.user, following_band=self.band).exists())

    def test_unfollow_band(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        FollowBand.objects.create(user=self.user, following_band=self.band)
        url = reverse('api:follow-list', args=[self.band.slug])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FollowBand.objects.filter(user=self.user, following_band=self.band).exists())


class FollowsViewTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user', password='password')
        cls.band1 = Band.objects.create(name="Test Band 1", slug="test-band-1")
        cls.band2 = Band.objects.create(name="Test Band 2", slug="test-band-2")
        FollowBand.objects.create(user=cls.user, following_band=cls.band1)

    def setUp(self):
        self.user_token = get_token_for_user(self.client, self.user.username, 'password')
        if not self.user_token:
            self.fail("Не удалось получить JWT токен")

    def test_follows_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('api:follows-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FollowBand.objects.filter(user=self.user).count(), 1)

    def test_follows_list_for_unauthorized(self):
        url = reverse('api:follows-list')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
