from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        max_length=200, unique=True, verbose_name='Почта')
    username = models.CharField(
        max_length=30, unique=True, verbose_name='Никнейм')
    password = models.CharField(
        max_length=100, verbose_name='Пароль')
    telegram_id = models.CharField(
        max_length=100, unique=True, null=True,
        blank=True, verbose_name='telegram ID')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='Users_profile',
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    bio = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='о себе'
    )
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        null=True,
        blank=True
    )
    favourite_subgenres = models.ManyToManyField(
        "reviews.SubGenre",
        max_length=50,
        blank=True,
        verbose_name='Любимые поджанры'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
