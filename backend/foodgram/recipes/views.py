from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import Recipes, Component
from .serializers import ComponentSerializer, RecipesSerializer


class ComponentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)