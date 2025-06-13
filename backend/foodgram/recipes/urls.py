from django.urls import include, path, re_path
from rest_framework import routers
from django_short_url import views as surl_views

from .views import (IngredientViewSet,
                    RecipesViewSet,
                    SubscriptionViewSet,
                    SingleSubscriptionViewSet)

router = routers.DefaultRouter()
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet)
router.register(r'users/subscriptions',
                SubscriptionViewSet,
                basename='subscriptions')
router.register(r'users', SingleSubscriptionViewSet, basename='users')

urlpatterns = [
    re_path(r's/^(?P<surl>\w+)', surl_views.short_url_redirect,
            name='short_url_redirect'),
    path('', include(router.urls)),
]