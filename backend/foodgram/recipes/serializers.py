from django.core.paginator import Paginator
from rest_framework import serializers
from .models import Recipes, Ingredient, RecipesIngredient
from users.serializers import UsersSerializer
from base64 import b64decode
import uuid
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f"avatar_{uuid.uuid4().hex[:8]}.{ext}"
            data = ContentFile(b64decode(imgstr), name=filename)
        return super().to_internal_value(data)

class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeCreateSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(min_value=1)

class RecipesSerializer(serializers.ModelSerializer):
    cooking_time = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Cooking time must be greater than zero!'
        }
    )

    author = UsersSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited',
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart',
        read_only=True
    )

    class Meta:
        model = Recipes
        fields = ('id', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('is_favorited', 'is_in_shopping_cart', 'author')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientRecipeSerializer(
            instance.recipe_ingredients.all(), many=True
        ).data
        return representation

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return IngredientRecipeSerializer(ingredients, many=True).data

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if 'ingredients' in data:
            ret['ingredients'] = data['ingredients']
        return ret

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Cooking time must be greater than zero!')
        return value

    def validate_ingredients(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Ingredients must be a list!")

        if not value:
            raise serializers.ValidationError(
                "At least one ingredient is required!")

        ingredient_ids = [item.get('id') for item in value]
        if None in ingredient_ids:
            raise serializers.ValidationError(
                "Each ingredient must have an id")

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ingredients must not be duplicated!")

        return value

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user_favs.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.shopping_carts.filter(user=request.user).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        if not ingredients_data or len(ingredients_data) == 0:
            raise serializers.ValidationError(
                'Ingredients field must be provided!'
            )

        recipe = Recipes.objects.create(**validated_data)
        self.create_ingredients(recipe=recipe, ingredients_data=ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if not ingredients_data or len(ingredients_data) == 0:
            raise serializers.ValidationError(
                'Ingredients field must be provided!'
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            self.update_ingredients(instance, ingredients_data)

        return instance

    def create_ingredients(self, recipe, ingredients_data):
        ingredient_ids = [item['id'] for item in ingredients_data]
        ingredients = Ingredient.objects.in_bulk(ingredient_ids)
        if len(ingredients) != len(ingredient_ids):
            raise serializers.ValidationError(
                'Ingredient does not exist!'
            )

        ingredient_recipe_objects = []
        for ingredient_data in ingredients_data:
            if ingredient_data['id'] in ingredients:
                if int(ingredient_data['amount']) <= 0:
                    raise serializers.ValidationError(
                        'Amount cannot be less than 1!'
                    )

                ingredient_recipe_objects.append(
                    RecipesIngredient(
                        recipe=recipe,
                        ingredient=ingredients[ingredient_data['id']],
                        amount=ingredient_data['amount']
                    )
                )
        RecipesIngredient.objects.bulk_create(ingredient_recipe_objects)

    def update_ingredients(self, recipe, ingredients_data):
        recipe.recipe_ingredients.all().delete()
        self.create_ingredients(recipe, ingredients_data)

class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Amount must be greater than zero!'
        }
    )

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')

class SubscriptionSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = [*UsersSerializer.Meta.fields, 'recipes', 'recipes_count']

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            paginator = Paginator(recipes, recipes_limit)
            recipes = paginator.page(1).object_list

        return ShortRecipeSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()