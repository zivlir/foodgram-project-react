from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (AuthorViewSet, FavoriteViewSet, IngredientsViewSet,
                    RecipeViewSet, ShoppingViewSet, TagViewSet)

v1_router = SimpleRouter()
v1_router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register('users/subsciptions', AuthorViewSet, basename='follows')


urlpatterns = [
    path('users/<int:author_id>/subscribe/', AuthorViewSet),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet, name='add_to_favorites'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingViewSet, name='add_to_shop'
    ),
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
