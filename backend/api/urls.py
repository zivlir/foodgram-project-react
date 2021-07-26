from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (AuthorViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingViewSet, TagViewSet, FollowViewSet, FollowListViewSet)

v1_router = SimpleRouter()
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register('users/subsciptions', FollowListViewSet, basename='follows')


urlpatterns = [
    path(
        'users/<int:author_id>/subscribe/',
        FollowViewSet.as_view(), name='subscribe'
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view(), name='add_to_favorites'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingViewSet.as_view(), name='add_to_shop'
    ),
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
