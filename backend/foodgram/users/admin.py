from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Follow


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('follower', 'following')
