from rest_framework import serializers
from image64conv.serializers import Base64ImageField
from .models import UserProfile, Subscription
from allauth.account.serializers import UserSerializer, UserCreateSerializer

class UserProfileSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = UserProfile
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or obj == request.user:
            return False
        return Subscription.objects.filter(user=request.user, follower=obj).exists()

class UserProfileCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = UserProfile
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name')