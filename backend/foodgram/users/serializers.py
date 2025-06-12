from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from .models import User, Subscription
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            _, b64_data = data.split(';base64,')
            ext = _.split('/')[-1]
            data = ContentFile(b64decode(b64_data), name=f"temp.{ext}")
        return super().to_internal_value(data)


class UsersSerializer(UserSerializer):
    is_following = serializers.SerializerMethodField(
        'check_is_following',
        read_only=True
    )
    profile_pic = Base64ImageField(required=False, allow_null=True)
    profile_pic_url = serializers.SerializerMethodField(
        'get_pic_url',
        read_only=True,
    )

    class Meta:
        model = User
        read_only_fields = (
            'account',
            'is_following')

    def get_pic_url(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None

    def get_authenticated_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user

    def check_is_following(self, obj):
        auth_user = self.get_authenticated_user()
        return Follow.objects.filter(
            follower=auth_user, followed=obj).exists()
    
    @action(detail=True, methods=['delete'], url_path='avatar')
    def delete_avatar(self, instance):
        instance.avatar = None
        instance.save()
        return instance
    
    @action(detail=True, method=['put'], url_path='avatar')
    def put_avatar(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
    
class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        read_only_field = ('user', 'follows')