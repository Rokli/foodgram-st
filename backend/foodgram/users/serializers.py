from rest_framework import serializers
from dishes.serializers import Base64ImageField
from .models import User


class UsersSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('username', 'is_subscribed')

    def get_avatar_url(self, obj):
        return obj.avatar.url if obj.avatar else None