import uuid
from base64 import b64decode

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from .models import User, Follow


class ImageBase64Field(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_part, image_string = data.split(';base64,')
            extension = format_part.split('/')[-1]
            file_name = f"user_avatar_{uuid.uuid4().hex[:8]}.{extension}"
            data = ContentFile(b64decode(image_string), name=file_name)
        return super().to_internal_value(data)


class UsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = ImageBase64Field(
        source='profile_picture',
        required=False, 
        allow_null=True
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 
            'last_name', 'is_subscribed', 'avatar'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if (not request or not request.user.is_authenticated 
                or obj == request.user):
            return False
        return Follow.objects.filter(
            follower=request.user, following=obj
        ).exists()


class UsersCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'password', 
            'first_name', 'last_name'
        )