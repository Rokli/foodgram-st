from base64 import b64decode
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Recipe, Ingredient, IngredientRecipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            _, b64_data = data.split(';base64,')
            ext = _.split('/')[-1]
            data = ContentFile(b64decode(b64_data), name=f"temp.{ext}")
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipesSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=True)
    image = Base64ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if not ingredients_data:
            raise serializers.ValidationError(_('Ingredients field is required.'))
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(**ingredient_data)
            IngredientRecipe.objects.create(ingredient=ingredient, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        ingredients_data = validated_data.pop('ingredients', None)
        if not ingredients_data:
            raise serializers.ValidationError(_('Ingredients field is required.'))
        instance.achievements.clear()
        for ingredient_data in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(**ingredient_data)
            IngredientRecipe.objects.create(ingredient=ingredient, recipe=instance)
        instance.save()
        return instance