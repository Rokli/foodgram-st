from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters as df_filters
from .models import Recipe
from .serializers import RecipeSerializer


class RecipeFilter(FilterSet):
    is_favorited = df_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = df_filters.BooleanFilter(method='filter_is_in_shopping_cart')
    author = df_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context