from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Recipes, Component
from .serializers import ComponentSerializer, RecipesSerializer
from .permissions import AuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

class ComponentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'is_favorited', 'is_in_shopping_cart')
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)