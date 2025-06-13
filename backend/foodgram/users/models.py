from re import match
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.validators import ValidationError


def validate_username(value):
    if not match(r'^[\w.@+-]+\z', value):
        raise ValidationError('Invalid characters in username')

class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=150, unique=True, validators=[validate_username])
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    avatar = models.ImageField(upload_to='profiles/avatars/', null=True, default=None)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta(AbstractUser.Meta):
        db_table = 'auth_users'
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'

class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'follower'], name="unique_follow")
        ]
        verbose_name = 'subscription'
        verbose_name_plural = 'subscriptions'