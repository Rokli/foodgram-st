from base64 import b64decode
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Recipes, Component, RecipesComponent


class Base64PhotoField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            head, b64_data = data.split(';base64,')
            ext = head.split('/')[-1]
            data = ContentFile(b64decode(b64_data), name=f"img.{ext}")
        return super().to_internal_value(data)


class ComponentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name')

    class Meta:
        model = Component
        fields = ('id', 'name', 'measure')


class RecipesSerializer(serializers.ModelSerializer):
    components = ComponentSerializer(many=True, required=True)
    photo = Base64PhotoField(required=False, allow_null=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = '__all__'

    def get_photo_url(self, obj):
        return obj.photo.url if obj.photo else None

    def create(self, validated_data):
        if 'components' not in self.initial_data:
            raise serializers.ValidationError('Не указаны компоненты.')

        comp_data = validated_data.pop('components')
        recipe = Recipes.objects.create(**validated_data)

        for comp in comp_data:
            comp_obj, _ = Component.objects.get_or_create(**comp)
            RecipesComponent.objects.create(dish=recipe, component=comp_obj, amount=1)  # 1 по умолчанию

        return recipe

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.desc = validated_data.get('desc', instance.desc)
        instance.time = validated_data.get('time', instance.time)
        instance.photo = validated_data.get('photo', instance.photo)

        if 'components' not in validated_data:
            raise serializers.ValidationError('Не указаны компоненты.')

        comps = validated_data.pop('components')
        RecipesComponent.objects.filter(dish=instance).delete()

        for comp in comps:
            comp_obj, _ = Component.objects.get_or_create(**comp)
            RecipesComponent.objects.create(dish=instance, component=comp_obj, amount=1)

        instance.save()
        return instance
