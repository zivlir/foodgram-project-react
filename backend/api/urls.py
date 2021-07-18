from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings

from .views import IngredientsViewSet, RecipeViewSet, TagViewSet, FavoriteViewSet, ShoppingViewSet

v1_router = DefaultRouter()
v1_router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'users/subsciptions', FavoriteViewSet, basename='favorites')
v1_router.register(r'users/(?P<user_id>\d+)/subscripe', FavoriteViewSet, basename='subscribe')


urlpatterns = [
    path('', include(v1_router.urls)),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
