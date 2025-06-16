from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator,MaxValueValidator
from django.db import models
from django.urls import reverse

User = get_user_model()
MIN_AMOUNT = 1
MAX_AMOUNT = 32_000

class IngredientModel(models.Model):
    title = models.CharField(max_length=256, verbose_name='Название')
    measurement_unit = models.CharField(
        default='г.',
        max_length=30,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.title} ({self.measurement_unit})'


class Recipe(models.Model):
    title = models.CharField(max_length=256, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT)
        ],
        verbose_name='Время приготовления'
    )
    picture = models.ImageField(
        upload_to='recipe_images/',
        verbose_name='Изображение'
    )
    creator = models.ForeignKey(
        User,
        related_name='created_recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    components = models.ManyToManyField(
        IngredientModel,
        through='RecipeIngredient',
        related_name='used_in_recipes',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты'
    )
    publication_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-publication_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_amounts',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        IngredientModel,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    quantity = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT)
        ],
        verbose_name='Количество'
    )

    class Meta:
        ordering = ['recipe', 'ingredient']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_per_recipe'
            )
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient} в рецепте {self.recipe}'


class ShoppingCart(models.Model):
    owner = models.ForeignKey(
        User,
        related_name='shopping_items',
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_carts',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['owner', 'recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'owner'],
                name='unique_recipe_in_cart'
            )
        ]
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    def __str__(self):
        return f'{self.recipe} в корзине у {self.owner}'


class FavoriteRecipe(models.Model):
    owner = models.ForeignKey(
        User,
        related_name='favorite_recipes',
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorited_by',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['owner', 'recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'owner'],
                name='unique_favorite_recipe'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.recipe} в избранном у {self.owner}'