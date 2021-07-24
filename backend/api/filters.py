from distutils.util import strtobool

import django_filters as filters

from api.models import FavorRecipes, Recipe, Tag

FILTER_CHOICES = (
    (0, 'True'),
    (1, 'False'),
)


class RecipeFilter(filters.FilterSet):
    """
    Класс фильтрации контента по заданным параметрам: только избранное, либо
    добавленное в корзину. Логика работы аналогична RecipeSerilializer
    """
    # Yet, works only with True/False params - find out a way make
    # it work with digits
    is_favorited = filters.BooleanFilter(method='get_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shop_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def get_shop_cart(self, query, name, value):
        user = self.request.user
        if self.request and value:
            return Recipe.objects.filter(author__author=user)
        return Recipe.objects.all()

    def get_favorited(self, query, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorite_recipes__author=user)
        return Recipe.objects.all()
