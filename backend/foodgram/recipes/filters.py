from .models import Recipe
from django_filters import rest_framework as filters


class RecipeFilter(filters.FilterSet):
    fav_flag = filters.BooleanFilter(method='filter_fav_flag')
    cart_flag = filters.BooleanFilter(method='filter_cart_flag')

    class Meta:
        model = Recipe
        fields = ['author', 'name']

    def filter_fav_flag(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(user_favs__user=self.request.user)
        return queryset

    def filter_cart_flag(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset