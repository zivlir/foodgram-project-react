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
    добавленное в корзину (включающие и исключающие запросы).
    В остальном, логика работы аналогична RecipeSerilializer
    """
    is_favorited = filters.ChoiceFilter(
        choices=FILTER_CHOICES, method='get_favorited'
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=FILTER_CHOICES, method='get_shop_cart'
    )
    tags = filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def get_shop_cart(self, queryset, name, value):
        user = self.request.user
        if value == 1 and not user.is_anonymous:
            return Recipe.objects.filter(shop_list__author=user)
        elif value == 0 and not user.is_anonymous:
            return Recipe.objects.exclude(shop_list__author=user)
        return Recipe.objects.all()

    def get_favorited(self, queryset, name, value):
        user = self.request.user
        if value == 1 and not user.is_anonymous:
            return Recipe.objects.filter(favorite_recipes__author=user)
        elif value == 0 and not user.is_anonymous:
            return Recipe.objects.exclude(favorite_recipes__author=user)
        return Recipe.objects.all()

