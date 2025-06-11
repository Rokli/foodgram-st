from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'is_subscribed')
        read_only_fields = ('id', 'is_subscribed')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user

    def validate(self, data):
        if len(data.get('username', '')) > 150:
            raise serializers.ValidationError({'username': ['Username must be 150 characters or fewer.']})
        if len(data.get('first_name', '')) > 150:
            raise serializers.ValidationError({'first_name': ['First name must be 150 characters or fewer.']})
        if len(data.get('last_name', '')) > 150:
            raise serializers.ValidationError({'last_name': ['Last name must be 150 characters or fewer.']})
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError('Both email and password are required.')

        data['user'] = user
        return data