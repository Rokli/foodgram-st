from django.urls import include, path

urlpatterns = [
    path('', include('recipes.urls')),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]