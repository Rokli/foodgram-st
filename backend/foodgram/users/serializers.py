from rest_framework import serializers
from dishes.serializers import Base64ImageField
from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from .models import User, Subscription


class UsersSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('username', 'is_subscribed')

    def get_avatar_url(self, obj):
        return obj.avatar.url if obj.avatar else None
    
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        read_only_fields = ('subscriber', 'followed_user')

    def create(self, validated_data):
        current_user = UsersSerializer.get_authenticated_user()
        if current_user is None:
            return status.HTTP_401_UNAUTHORIZED
        if 'followed_user' not in self.initial_data:
            raise serializers.ValidationError(
                'Поле "followed_user" обязательно для заполнения!'
            )
        user_id = validated_data.pop('followed_user')
        target_user = get_object_or_404(User, id=user_id)
        existing_subscription = Subscription.objects.filter(subscriber=current_user, followed_user=target_user).first()
        if existing_subscription:
            return status.HTTP_400_BAD_REQUEST
        return super().create(validated_data)