from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    username = models.CharField(
        max_length=150,
        unique=True,
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
    )

    email = models.EmailField(
        unique=True,
        max_length=254
    )
    avatar = models.ImageField(
        upload_to='users/images',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    class Meta:
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'


class Subscription(models.Model):
    user = models.ForeignKey(
        'User',
        related_name='subscriptions',
        on_delete=models.CASCADE
    )
    follows = models.ForeignKey(
        'User',
        related_name='Подписка',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'follows'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'