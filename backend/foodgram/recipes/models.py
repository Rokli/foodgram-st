from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator

User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(default='г.', max_length=30)

    class Meta:
        ordering = ['name']
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

class Recipes(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    image = models.ImageField(upload_to='recipes/images')
    author = models.ForeignKey(User, related_name='recipes', on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipesIngredient', 
        related_name='recipes',
        through_fields=('recipe', 'ingredient'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes-detail', kwargs={'pk': self.pk})

class RecipesIngredient(models.Model):
    recipe = models.ForeignKey(Recipes, related_name='recipe_ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'], name='unique_recipe_ingredient')
        ]

class ItemCart(models.Model):
    user = models.ForeignKey(User, related_name='cart', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, related_name='shopping_carts', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'], name='unique_recipe_user')
        ]

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'

class Favorites(models.Model):
    user = models.ForeignKey(User, related_name='favs', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, related_name='user_favs', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'], name='unique_recipe_user_fav')
        ]

    def __str__(self):
        return f'{self.recipe} в избранном {self.user}'