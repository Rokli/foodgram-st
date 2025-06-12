from rest_framework import serializers
from dishes.serializers import Base64ImageField
from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from .models import User, Subscription
from rest_framework.decorators import action
from rest_framework import serializers

class UserseSerializer(UserSerializer):
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
        model = Account
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
    def delete_avatar(self, request, pk=None):
        user = self.get_object()
    
    @action(method=['put'], url_path='avatar')
    def put_avatar(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance