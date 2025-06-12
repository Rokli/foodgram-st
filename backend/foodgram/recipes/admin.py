from django.contrib import admin
from .models import Recipes, Ingredient,RecipesIngredient


admin.site.register(Ingredient)
admin.site.register(Recipes)
admin.site.register(RecipesIngredient)