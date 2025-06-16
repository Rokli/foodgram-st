from base64 import b64decode
import uuid

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from rest_framework import serializers

from .models import Recipe, IngredientModel, RecipeIngredient
from users.serializers import UsersSerializer


MIN_AMOUNT = 1
MAX_AMOUNT = 32000

class ImageBase64Field(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_part, image_string = data.split(';base64,')
            extension = format_part.split('/')[-1]
            file_name = f"recipe_img_{uuid.uuid4().hex[:10]}.{extension}"
            data = ContentFile(b64decode(image_string), name=file_name)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='title')

    class Meta:
        model = IngredientModel
        fields = ('id', 'name', 'measurement_unit')
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['measurement_unit'] = instance.measurement_unit
        return representation


class RecipeIngredientCreateSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=IngredientModel.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT,
        error_messages={
            'min_value': f'Количество должно быть не менее {MIN_AMOUNT}',
            'max_value': f'Количество должно быть не более {MAX_AMOUNT}'
        }
    )

class RecipeSerializer(serializers.ModelSerializer):
    cooking_time = serializers.IntegerField(
        source='cooking_time',
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT,
        error_messages={
            'min_value': f'Время приготовления должно быть не меньше {MIN_AMOUNT} минут!',
            'max_value': f'Время приготовления не может превышать {MAX_AMOUNT} минут!'
        }
    )
    creator = UsersSerializer(source='creator', read_only=True)
    components = serializers.SerializerMethodField()
    picture = ImageBase64Field(source='picture', required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'creator', 'components', 'is_favorited',
            'is_in_shopping_cart', 'name', 'picture', 'text', 'cooking_time'
        )
        read_only_fields = ('is_favorited', 'is_in_shopping_cart', 'creator')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.title
        representation['text'] = instance.description
        representation['cooking_time'] = instance.cooking_time
        representation['author'] = representation.pop('creator')
        representation['image'] = representation.pop('picture')
        representation['ingredients'] = RecipeIngredientSerializer(
            instance.ingredient_amounts.all(), many=True
        ).data
        return representation

    def get_components(self, obj):
        ingredient_relations = obj.ingredient_amounts.all()
        return RecipeIngredientSerializer(ingredient_relations, many=True).data

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        if 'ingredients' in data:
            internal_data['ingredients'] = data['ingredients']
        return internal_data

    def validate_ingredients(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Ингредиенты должны быть переданы в виде списка!"
            )

        if not value:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один ингредиент!"
            )

        ingredient_ids = [item.get('id') for item in value]
        if None in ingredient_ids:
            raise serializers.ValidationError(
                "Каждый ингредиент должен иметь корректный id"
            )

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться!"
            )

        return value

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorited_by.filter(owner=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.in_carts.filter(owner=request.user).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        if not ingredients_data or len(ingredients_data) == 0:
            raise serializers.ValidationError(
                'Поле ингредиентов обязательно для заполнения!'
            )

        recipe_data = {
            'title': validated_data.get('name', ''),
            'description': validated_data.get('text', ''),
            'cooking_time': validated_data.get('cooking_time', validated_data.get('cooking_time')),
            'picture': validated_data.get('image', validated_data.get('picture')),
            'creator': validated_data.get('author', validated_data.get('creator'))
        }
        
        recipe = Recipe.objects.create(**recipe_data)
        self._create_ingredients_relations(recipe=recipe, ingredients_data=ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if not ingredients_data:
            raise serializers.ValidationError(
                'Поле ингредиентов обязательно для заполнения!'
            )

        if 'name' in validated_data:
            instance.title = validated_data['name']
        if 'text' in validated_data:
            instance.description = validated_data['text']
        if 'cooking_time' in validated_data:
            instance.cooking_time = validated_data['cooking_time']
        if 'image' in validated_data:
            instance.picture = validated_data['image']
            
        instance.save()

        if ingredients_data is not None:
            self._update_ingredients_relations(instance, ingredients_data)

        return instance

    def _create_ingredients_relations(self, recipe, ingredients_data):
        ingredient_ids = [item['id'] for item in ingredients_data]
        ingredients = IngredientModel.objects.in_bulk(ingredient_ids)
        
        if len(ingredients) != len(ingredient_ids):
            raise serializers.ValidationError(
                'Один или несколько ингредиентов не существует!'
            )

        ingredient_relations = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            try:
                amount = int(ingredient_data['amount'])
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f'Количество ингредиента (ID: {ingredient_id}) должно быть целым числом!'
                )
            ingredient_relations.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredients[ingredient_id],
                    quantity=amount
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_relations)

    def _update_ingredients_relations(self, recipe, ingredients_data):
        recipe.ingredient_amounts.all().delete()
        self._create_ingredients_relations(recipe, ingredients_data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.title')
    measurement_unit = serializers.CharField(source='measurement_unit')
    amount = serializers.IntegerField(
        source='quantity',
        min_value=1,
        error_messages={
            'min_value': 'Количество должно быть больше нуля!'
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CompactRecipeSerializer(serializers.ModelSerializer):
    image = ImageBase64Field(source='picture', required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.title
        representation['cooking_time'] = instance.cooking_time
        return representation


class FollowingSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = [*UsersSerializer.Meta.fields, 'recipes', 'recipes_count']

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.created_recipes.all()

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            paginator = Paginator(recipes, recipes_limit)
            recipes = paginator.page(1).object_list

        return CompactRecipeSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.created_recipes.count()