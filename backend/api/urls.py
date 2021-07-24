from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import (AuthorViewSet, FavoriteViewSet, IngredientsViewSet,
                    RecipeViewSet, ShoppingViewSet, TagViewSet)

v1_router = SimpleRouter()
v1_router.register(
    r'ingredients', IngredientsViewSet,
    basename='ingredients'
)
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
    basename='favorite-detail'
)
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'users/subsciptions', AuthorViewSet, basename='follow')
v1_router.register(
    r'users/(?P<author_id>\d+)/subscribe', AuthorViewSet ,
    basename='new_follow'
)


urlpatterns = [
    # path('users/<int:author_id>/subscribe/', FollowViewSet.as_view(), name='new_follow'),
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
