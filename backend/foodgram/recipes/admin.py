from django.contrib import admin

from .models import Recipe, IngredientModel, RecipeIngredient


@admin.register(IngredientModel)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit')
    search_fields = ('title',)
    list_filter = ('unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'cooking_time', 'publication_date')
    search_fields = ('title', 'creator__username')
    list_filter = ('publication_date', 'cooking_time')
    readonly_fields = ('publication_date',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity')
    list_filter = ('ingredient',)