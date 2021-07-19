from rest_framework import filters, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from api.models import (FavorRecipes, Follow, Ingridient, Recipe,
                        RecipeComponent, ShoppingList, Tag, User)
from api.serializers import RecipeSerializer, FavorSerializer, ShoppingSerializer, TagSerializer, IngidientSerializer, FollowSerializer
from api.permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

class GetPostViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass

class GetPostDelViewSet(mixins.CreateModelMixin,
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


# class FollowViewSet(APIView):
#     def get(self, request):
#         obj = Follow.objects.all()
#         serializer = FollowSerializer(obj, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = FollowSerializer(data=request.data)
#         author = get_object_or_404(User, pk=self.kwargs.get('id'))
#         if serializer.is_valid():
#             serializer.save(user=self.request.user, author=author)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
class FollowViewSet(GetPostDelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
