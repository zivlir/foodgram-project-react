from django.db.models import Exists, OuterRef, Value
from djoser import views
from rest_framework import filters, mixins, status, viewsets, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.filters import RecipeFilter, IngredientFilter
from api.models import (FavorRecipes, Follow, Ingredient, Recipe,
                        RecipeComponent, ShoppingList, Tag)
from users.models import User
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (
    FavorSerializer, FollowReadSerializer, IngredientSerializer,
    FollowerReadSerializer, FollowSerializer,
    ListSubscriptionsSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, ShoppingSerializer,
    TagSerializer, UserSerializer
)
from users.serializers import UserSerializer

class GetPostViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class GetPostDelViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pass



class RecipeViewSet(viewsets.ModelViewSet):
    filter_class = RecipeFilter
    permission_classes = [IsOwnerOrReadOnly, ]

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()
        if user.is_anonymous:
            return queryset
        else:
            queryset = queryset.annotate(
            is_favorited=Exists(FavorRecipes.objects.filter(
                author=user, recipes_id=OuterRef('pk')
            )),
            is_in_shopping_list=Exists(ShoppingList.objects.filter(
                author=user, recipe_id=OuterRef('pk')
            ))
        )
        _favorited = self.request.query_params.get('is_favorited')
        _in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )

        # Обрабатываем запрос как строки, чтобы не начать фильтрацию при
        # отсутствии параметра
        if _favorited == 'true':
            queryset = queryset.filter(is_favorited=True)
        elif _favorited == 'false':
            queryset = queryset.filter(is_favorited=False)
        if _in_shopping_cart == 'true':
            queryset = queryset.filter(is_in_shopping_list=True)
        elif _in_shopping_cart == 'false':
            queryset = queryset.exclude(is_in_shopping_list=True)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


    def get_serializer_class(self):
        if self.request.method in ['GET', ]:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_class = IngredientFilter
    search_fields = ['name', ]
    pagination_class = None


class FavoriteViewSet(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavorSerializer

    # def perform_create(self, recipe_id):
    #     recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
    #     serializer.save(author=self.request.user, recipe=recipe)

    def get(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {
            'author': user.id,
            'recipes': recipe.id
        }
        serializer = FavorSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite_obj = get_object_or_404(
            FavorRecipes, author=user, recipes=recipe
        )
        favorite_obj.delete()
        return Response(
            'Removed', status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class ShoppingViewSet(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingSerializer

    def get(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingList.objects.create(user=user, recipe=recipe)
        serializer = FavorSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_list_obj = get_object_or_404(
            ShoppingList, user=user, recipe=recipe)
        shopping_list_obj.delete()
        return Response(
            'Deleted', status=status.HTTP_204_NO_CONTENT)


class AuthorViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


# @api_view(http_method_names=['GET', ])
# @permission_classes([IsAuthenticated])
# def FollowListView(request):
#     user = User.objects.filter(following__user=request.user)
#     paginator = PageNumberPagination()
#     paginator.page_size = 10  # change to PAGE_SIZE
#     response = paginator.paginate_queryset(user, request)
#     serializer = ListSubscriptionsSerializer(
#         response, many=True, context={'current_user': request.user}
#     )
#     return paginator.get_paginated_response(serializer.data)

class FollowViewSet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, author_id):
        user = request.user
        data = {
            'user': user.id,
            'author': author_id
        }
        serializer = FollowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        follow = get_object_or_404(
            Follow, user_id=user.id, author_id=author_id
        )
        follow.delete()
        return Response('Вы успешно отписаны',
                        status=status.HTTP_204_NO_CONTENT)

class FollowReadViewSet(ListAPIView):
    queryset = User.objects.all()
    serializer_class = FollowReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
