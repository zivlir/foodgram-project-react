from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, FollowViewSet, IngredientsViewSet,
                    RecipeViewSet, ShoppingViewSet, TagViewSet)

v1_router = DefaultRouter()
v1_router.register(
    r'ingredients', IngredientsViewSet,
    basename='ingredients'
)
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
    basename='favorites'
)
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'users/subsciptions', FollowViewSet, basename='follow')
v1_router.register(
    r'users/(?P<user_id>\d+)/subscripe', FollowViewSet,
    basename='follow'
)


urlpatterns = [
    # path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

