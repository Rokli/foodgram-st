from django.urls import include, path
from rest_framework.authtoken import views

urlpatterns = [
    path('', include('djoser.urls.base')),
    path('auth/', include('djoser.urls.authtoken')),
    #path('auth/', include('djoser.urls.jwt')),
]