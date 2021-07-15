from django.shortcuts import render
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import mixins, filters
from rest_framework.viewsets import ModelViewSet
from django.db import models

from .models import Recipe, Ingridient, FavorRecipes, Tag, RecipeComponent, Follow, ShoppingList
from .serializers import RecipeSerializer


class RecipeViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(favorite__author=user)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingridient.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['pk', '^name']

