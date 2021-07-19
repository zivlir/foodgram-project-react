from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.models import (FavorRecipes, Follow, Ingridient, Recipe,
                        RecipeComponent, ShoppingList, Tag, User)
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (FavorSerializer, FollowSerializer,
                             IngidientSerializer, RecipeSerializer,
                             ShoppingSerializer, TagSerializer)


class GetPostViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class GetPostDelViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pass


class RecipeViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, ]
    # queryset = Recipe.objects.prefetch_related('favorite__author')
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'tags']


class IngredientsViewSet(GetPostViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngidientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['pk', '^name']


class FavoriteViewSet(GetPostDelViewSet):
    queryset = FavorRecipes.objects.all()
    serializer_class = FavorSerializer
    permission_classes = [IsAuthenticated]


class TagViewSet(GetPostViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ShoppingViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(author=self.request.user, recipe=recipe)


class FollowViewSet(GetPostDelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
