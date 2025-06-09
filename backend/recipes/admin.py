from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'author__username')
    list_filter = ('author',)

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)