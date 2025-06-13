from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilterSet(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_favorited_recipes')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_cart_recipes')

    class Meta:
        model = Recipe
        fields = ['creator', 'title']

    def filter_favorited_recipes(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorited_by__owner=self.request.user)
        return queryset

    def filter_cart_recipes(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_carts__owner=self.request.user)
        return queryset