from io import BytesIO
from django.db.models import Sum
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status, mixins, pagination
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipes, Ingredient, ItemCart, RecipesIngredient, Favorites
from .serializers import IngredientSerializer, RecipesSerializer, ShortRecipeSerializer, SubscriptionSerializer
from .permissions import AuthorOrReadOnly
from .filters import RecipeFilter
from users.models import Subscription, User

User = get_user_model()

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', )
    search_fields = ('^name', )

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name.lower())
        return self.queryset

class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipesSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    filterset_fields = ('name', )
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.select_related('author').prefetch_related(
            'recipe_ingredients__ingredient',
            'user_favs',
            'shopping_carts'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart', permission_classes=[permissions.IsAuthenticated])
    def post_delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == 'POST':
            note, created = ItemCart.objects.get_or_create(user=user, recipe=recipe)
            if not created:
                return Response({
                    'message': 'Recipe already in cart!',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            count, _ = ItemCart.objects.filter(user=user, recipe=recipe).delete()
            if count == 0:
                return Response(
                    {'detail': 'Recipe not in cart!'},
                    status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart', permission_classes=[permissions.IsAuthenticated])
    def download_cart(self, request):
        user = request.user
        cart_items = RecipesIngredient.objects.filter(
            recipe__shopping_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        if not cart_items.exists():
            return Response({
                'message': 'Cart is empty',
                'status': 'success'
            }, status=status.HTTP_200_OK)

        file_content = BytesIO()
        line = ''
        for item in cart_items:
            line += (
                f"{item['ingredient__name']} - "
                f"{item['total_amount']} "
                f"{item['ingredient__measurement_unit']}\n"
            )
        file_content.write(line.encode('utf-8'))
        file_content.seek(0)
        response = FileResponse(
            file_content,
            content_type='text/plain',
            as_attachment=True,
            filename='cart_list.txt'
        )
        return response

    @action(detail=True, methods=['post', 'delete'], url_path='favorite', permission_classes=[permissions.IsAuthenticated])
    def post_delete_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == 'POST':
            note, created = Favorites.objects.get_or_create(user=user, recipe=recipe)
            if not created:
                return Response({
                    'message': 'Recipe already favorited!',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            count, _ = Favorites.objects.filter(user=user, recipe=recipe).delete()
            if count == 0:
                return Response({
                    'detail': 'Recipe not in favorites!'
                }, status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class SubscriptionViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SubscriptionSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return User.objects.filter(subbed_to__user=self.request.user).prefetch_related('recipes')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class SingleSubscriptionViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def sub_and_unsub(self, request, pk=None):
        to_sub = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if to_sub == request.user:
                return Response({'error': 'Cannot follow yourself!'}, status=status.HTTP_400_BAD_REQUEST)
            sub, created = Subscription.objects.get_or_create(user=request.user, follows=to_sub)
            if not created:
                return Response({'error': 'Already following!'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(to_sub)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        count, _ = Subscription.objects.filter(user=request.user, follows=to_sub).delete()
        if count == 0:
            return Response({'detail': 'Not following!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)