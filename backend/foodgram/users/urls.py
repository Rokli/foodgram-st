from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from .views import UsersViewSet

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls.base')),
    path('auth/', include('djoser.urls.authtoken')),
]