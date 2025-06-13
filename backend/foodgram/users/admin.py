from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription
from django.contrib import admin

admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
