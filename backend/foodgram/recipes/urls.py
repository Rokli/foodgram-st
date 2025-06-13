from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet, RecipeViewSet, 
    FollowingListViewSet, FollowManagementViewSet
)

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users/subscriptions', FollowingListViewSet, basename='subscriptions')
router.register(r'users', FollowManagementViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]