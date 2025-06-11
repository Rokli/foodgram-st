from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='users/images',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'


class Subscription(models.Model):
    user = models.ForeignKey(
        'User',
        related_name='subscriptions',
        on_delete=models.CASCADE
    )
    follower = models.ForeignKey(
        'User',
        related_name='followers',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'follower'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'