from django.contrib import UserAdmin
from .models import User, Subscription

admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
