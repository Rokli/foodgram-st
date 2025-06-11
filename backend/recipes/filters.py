import django_filters
from .models import Recipe

class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(method='filter_in_cart')
    author = django_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous or not value:
            return queryset
        return queryset.filter(favorited_by__user=user)

    def filter_in_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous or not value:
            return queryset
        return queryset.filter(shopping_cart__user=user)
