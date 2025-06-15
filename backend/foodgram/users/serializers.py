import uuid
from base64 import b64decode

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from .models import User
import re

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
        if (not request or not request.user.is_authenticated or obj == request.user):
            return False
        return obj.subscribers.filter(follower=request.user).exists()


class UsersCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name')

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+\z', value):
            raise serializers.ValidationError('Имя пользователя содержит недопустимые символы')
        return value

    def validate(self, data):
        if data.get('password') != data.get('re_password'):
            raise serializers.ValidationError({'re_password': 'Пароли не совпадают'})
        return data

    def create(self, validated_data):
        validated_data.pop('re_password', None)  
        return User.objects.create_user(**validated_data)