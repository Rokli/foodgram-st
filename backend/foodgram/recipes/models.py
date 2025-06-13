from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from rest_framework.validators import ValidationError

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(_('Название'), max_length=256)
    measurement_unit = models.CharField(
        ('Единица измерения'),
        default=_('г.'),
        null=False,
        max_length=30
    )

    class Meta:
        ordering = ['name']
        verbose_name = ('ингредиент')
        verbose_name_plural = ('Ингредиенты')

    def __str__(self):
        return self.name + ', ' + self.measurement_unit

class Recipes(models.Model):
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=256,
        blank=False
    )
    text = models.TextField(
        verbose_name=_('Описание'),
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_('Время приготовления (в минутах)'),
        blank=False,
        validators=[validate_positive,
                    MinValueValidator(1, message='Значение должно быть больше нуля!')],
    )
    image = models.ImageField(
        verbose_name=_('Фото'),
        upload_to='recipes/images',
        blank=False
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name=_('Автор'),
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name=_('Игредиенты'),
        related_name='recipes',
        through_fields=('recipe', 'ingredient'),
        blank=False,
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('рецепт')
        verbose_name_plural = _('Рецепты')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes-detail', kwargs={'pk': self.pk})


class RecipesIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        verbose_name=_('Рецепт'),
        related_name='recipe_ingredients',
        blank=False,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ингредиент'),
        blank=False,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        _('Количество'),
        blank=False,
        validators=[validate_positive,
                    MinValueValidator(1, message='Значение должно быть больше нуля!')],
    )

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

class ItemCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
        null=False
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Рецепт',
        null=False
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'
    
class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favs',
        verbose_name='Пользователь',
        null=False
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='user_favs',
        verbose_name='Рецепт',
        null=False
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user_fav'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном {self.user}'