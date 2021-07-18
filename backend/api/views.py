from django.db import models
from django.shortcuts import render
from rest_framework import filters, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from api.models import (FavorRecipes, Follow, Ingridient, Recipe,
                        RecipeComponent, ShoppingList, Tag)
from api.serializers import RecipeSerializer, FavorSerializer, ShoppingSerializer, TagSerializer, IngidientSerializer
from api.permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

class RecipeViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly, ]
    # queryset = Recipe.objects.prefetch_related('favorite__author')
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]

    # def get_queryset(self):
    #     queryset = Recipe.objects.all()
    #     tags = self.request.query_params.get('tags')
    #     user = self.request.user
    #     favor = self.request.query_params.get('is_favorited')
    #     in_shop_cart = self.request.query_params.get('is_in_shopping_cart')
    #     if tags is not None:
    #         queryset = queryset.filter(tags__slug__contains=tags)
    #     if user

    # def list(self, request, *args, **kwargs):
    #     queryset = Recipe.objects.all()
    #     if 'tags' in kwargs:
    #         self.queryset = queryset.filter(tags=kwargs['tags'])
    #     if self.request.user.is_authenticated:
    #         if 'is_favorited' in kwargs and kwargs['is_favorited'] == 1:
    #             self.queryset = self.queryset.filter(
    #                 favorite_recipes__author=self.request.user
    #             )
    #         if kwargs['is_in_shopping_cart'] == 1:
    #             self.queryset = self.queryset.filter(
    #                 shop_list__author=self.request.user
    #             )
    #     serializer = RecipeSerializer(queryset, many=True)
    #     return Response(serializer.data)

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

