from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from .models import Recipes, Ingredient
from .serializers import IngredientSerializer, RecipesSerializer
from .permissions import AuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name', )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all().order_by('created_at')
    serializer_class = RecipesSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    filterset_fields = ('author',
                        'name', 'is_in_shopping_cart', 'is_favorited')
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)