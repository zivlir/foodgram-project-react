from django.db.models import Exists, F, OuterRef
from django.http import HttpResponse
from djoser import views
from rest_framework import mixins, status, viewsets
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import UserSerializer

from api.filters import IngredientFilter, RecipeFilter
from api.models import (FavorRecipes, Follow, Ingredient, Recipe,
                        RecipeComponent, ShoppingList, Tag)
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (FavorSerializer, FollowReadSerializer,
                             FollowSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             ShoppingSerializer, TagSerializer)


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
            queryset = queryset.exclude(is_in_shopping_list=False)
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
        author = request.user.id
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {
            'author': author,
            'recipe': recipe.id
        }
        serializer = ShoppingSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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


class ShoppingCartDL(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        shop_list = {}
        cart = ShoppingList.objects.select_related('recipe').annotate(
            ingredients=F('recipe__ingredients')
        )
        for record in cart:
            recipe = record.recipe
            ingredients = RecipeComponent.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amt = ingredient.amount
                name = ingredient.ingredient.name
                units = ingredient.ingredient.units
                if name not in shop_list:
                    shop_list[name] = {
                        'measurement_unit': units,
                        'amount': amt
                    }
                else:
                    shop_list[name]['amount'] = (
                                shop_list[name]['amount'] +
                                amt)
        wishlist = []
        for item in shop_list:
            wishlist.append(
                f'{item} - {shop_list[item]["amount"]} '
                f'{shop_list[item]["measurement_unit"]} \n'
            )
        wishlist.append('\n')
        wishlist.append('FoodGram, 2021')
        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
