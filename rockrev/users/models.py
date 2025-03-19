from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Пользователь."""
    email = models.EmailField("email", max_length=200, unique=True)
    username = models.CharField("username", max_length=30, unique=True)
    password = models.CharField('password', max_length=100)

    def __str__(self):
        return self.username