from io import BytesIO

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, status, mixins, pagination
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .filters import RecipeFilterSet
from .models import IngredientModel, ShoppingCart, RecipeIngredient, FavoriteRecipe, Recipe
from .permissions import CreatorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeSerializer, CompactRecipeSerializer, 
    FollowingSerializer
)
from users.models import Follow, User

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IngredientModel.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('title',)
    search_fields = ('^title',)

    def get_queryset(self):
        search_name = self.request.query_params.get('name')
        if search_name:
            return self.queryset.filter(title__istartswith=search_name.lower())
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (CreatorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('title',)
    filterset_fields = ('title',)
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        return Recipe.objects.select_related('creator').prefetch_related(
            'ingredient_amounts__ingredient',
            'favorited_by',
            'in_carts'
        ).order_by('-publication_date')

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(
        detail=True, 
        methods=['post', 'delete'], 
        url_path='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def manage_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        current_user = request.user
        
        if not current_user.is_authenticated:
            return Response(
                {'error': 'Требуется аутентификация'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == 'POST':
            cart_item, created = ShoppingCart.objects.get_or_create(
                owner=current_user, recipe=recipe
            )
            if not created:
                return Response({
                    'message': 'Рецепт уже находится в корзине!',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
            
            recipe.save()
            serializer = CompactRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        elif request.method == 'DELETE':
            deleted_count, _ = ShoppingCart.objects.filter(
                owner=current_user, recipe=recipe
            ).delete()
            if deleted_count == 0:
                return Response(
                    {'detail': 'Рецепт не найден в корзине!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, 
        methods=['get'], 
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def export_shopping_list(self, request):
        current_user = request.user
        cart_ingredients = RecipeIngredient.objects.filter(
            recipe__in_carts__owner=current_user
        ).values(
            'ingredient__title',
            'ingredient__unit'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('ingredient__title')

        if not cart_ingredients.exists():
            return Response({
                'message': 'Корзина пуста',
                'status': 'success'
            }, status=status.HTTP_200_OK)

        file_buffer = BytesIO()
        shopping_list = ''
        for item in cart_ingredients:
            shopping_list += (
                f"{item['ingredient__title']} - "
                f"{item['total_quantity']} "
                f"{item['ingredient__unit']}\n"
            )
        file_buffer.write(shopping_list.encode('utf-8'))
        file_buffer.seek(0)
        
        response = FileResponse(
            file_buffer,
            content_type='text/plain',
            as_attachment=True,
            filename='shopping_list.txt'
        )
        return response

    @action(
        detail=True, 
        methods=['post', 'delete'], 
        url_path='favorite',
        permission_classes=[permissions.IsAuthenticated]
    )
    def manage_favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        current_user = request.user
        
        if not current_user.is_authenticated:
            return Response(
                {'error': 'Требуется аутентификация'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == 'POST':
            favorite_item, created = FavoriteRecipe.objects.get_or_create(
                owner=current_user, recipe=recipe
            )
            if not created:
                return Response({
                    'message': 'Рецепт уже в избранном!',
                    'data': []
                }, status=status.HTTP_400_BAD_REQUEST)
            
            recipe.save()
            serializer = CompactRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        elif request.method == 'DELETE':
            deleted_count, _ = FavoriteRecipe.objects.filter(
                owner=current_user, recipe=recipe
            ).delete()
            if deleted_count == 0:
                return Response({
                    'detail': 'Рецепт не найден в избранном!'
                }, status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowingListViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    
    serializer_class = FollowingSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(
            subscribers__follower=self.request.user
        ).prefetch_related('created_recipes')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FollowManagementViewSet(viewsets.GenericViewSet):
    
    queryset = User.objects.all()
    serializer_class = FollowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def toggle_subscription(self, request, pk=None):
        target_user = get_object_or_404(User, pk=pk)
        
        if request.method == 'POST':
            if target_user == request.user:
                return Response(
                    {'error': 'Нельзя подписаться на самого себя!'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subscription, created = Follow.objects.get_or_create(
                follower=request.user, following=target_user
            )
            if not created:
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя!'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(target_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        deleted_count, _ = Follow.objects.filter(
            follower=request.user, following=target_user
        ).delete()
        if deleted_count == 0:
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя!'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)