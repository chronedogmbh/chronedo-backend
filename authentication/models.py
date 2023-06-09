from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    otp_secret_key = models.PositiveIntegerField(blank=True, null=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Email(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return self.email
