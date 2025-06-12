from django.contrib.auth import get_user_model
from django.db import models 

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Наименование', max_length=255)
    measure = models.CharField('Единица измерения', max_length=50,
                               help_text='Укажите единицу измерения')

    class Meta:
        verbose_name = 'Компонент'
        verbose_name_plural = 'Компоненты'

    def __str__(self):
        return str(self.name)


class Recipes(models.Model):
    title = models.CharField('Название рецепта', max_length=255)
    desc = models.TextField('Описание')
    time = models.PositiveSmallIntegerField('Время приготовления',
                                            help_text='Укажите время')

    photo = models.ImageField('Изображение блюда',
                              upload_to='recipes/photos',
                              null=True,
                              blank=True)

    creator = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name='dishes')

    components = models.ManyToManyField(Ingredient,
                                        through='RecipesIngredient',
                                        related_name='dishes')

    fav = models.BooleanField('В избранном', default=False)
    cart = models.BooleanField('В корзине', default=False)

    class Meta:
        verbose_name = 'блюдо'
        verbose_name_plural = 'блюда'

    def __str__(self):
        return f"Блюдо: {self.title}"


class RecipesIngredient(models.Model):
    dish = models.ForeignKey(Recipes, on_delete=models.CASCADE, verbose_name='Блюдо')
    component = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Компонент')
    amount = models.FloatField('Количество', help_text='Укажите число в выбранных единицах')

    class Meta:
        verbose_name = 'состав блюда'
        verbose_name_plural = 'состав блюд'

    def __str__(self):
        return f"{self.amount} x {self.component} -> {self.dish}"

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь',
        null=False
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='Рецепт',
        null=False
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'