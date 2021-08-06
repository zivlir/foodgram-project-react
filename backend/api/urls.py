from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.utils import ShoppingCartDL
from api.views import (FavoriteViewSet, FollowListView, FollowViewSet,
                       IngredientViewSet, RecipeViewSet, ShoppingViewSet,
                       TagViewSet)

v1_router = SimpleRouter()
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    path(
        'users/<int:author_id>/subscribe/',
        FollowViewSet.as_view(), name='subscribe'
    ),
    path(
        'users/subscriptions/',
        FollowListView, name='subscriptions'
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view(), name='add_to_favorites'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingViewSet.as_view(), name='add_to_shop'
    ),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartDL.as_view(), name='shopping_cart_dl'
    ),
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
