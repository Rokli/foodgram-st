import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.validators import ValidationError


def validate_user_name(value):
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError('Недопустимые символы в имени пользователя')


class User(AbstractUser):
    email = models.EmailField(
        unique=True, 
        max_length=255,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=150, 
        unique=True, 
        validators=[validate_user_name],
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=150, 
        blank=False, 
        null=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150, 
        blank=False, 
        null=False,
        verbose_name='Фамилия'
    )
    profile_picture = models.ImageField(
        upload_to='user_avatars/', 
        null=True, 
        default=None,
        verbose_name='Аватар'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta(AbstractUser.Meta):
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class Follow(models.Model):
    follower = models.ForeignKey(
        User, 
        related_name='following', 
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User, 
        related_name='subscribers', 
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'], 
                name="unique_subscription"
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.follower} подписан на {self.following}'