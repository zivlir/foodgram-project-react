from django.db import models
from django.shortcuts import render
from rest_framework import filters, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from api.models import (FavorRecipes, Follow, Ingridient, Recipe,
                        RecipeComponent, ShoppingList, Tag)
from api.serializers import RecipeSerializer, FavorSerializer, ShoppingSerializer, TagSerializer, IngidientSerializer
from api.permissions import IsOwnerOrReadOnly


class RecipeViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, ]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    # def retrieve(self, request, *args, **kwargs):
    #     if request.user.is_authenticated():
    #         user=self.request.user
    #         return Recipe.objects.prefetch_related('favorite__author')
    #         # return Recipe.objects.filter(favorite__author=user).select_related('author')
    #     else:
    #         return Recipe.objects.all()

    # описать создание, получение одного рецепта, обновление и удаление


class IngredientsViewSet(ModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngidientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['pk', '^name']


class FavoriteViewSet(ModelViewSet):
    queryset = FavorRecipes.objects.all()
    serializer_class = FavorSerializer
    permission_classes = [IsAuthenticated]


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class ShoppingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(author=self.request.user, recipe=recipe)

