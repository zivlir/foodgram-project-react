import django_filters as filters

from distutils.util import strtobool
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
    is_favorited = filters.TypedChoiceFilter(choices=FILTER_CHOICES,
                                             coerce=strtobool)
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shop_cart'
    )
    is_favorited = filters.ModelChoiceFilter(queryset=FavorRecipes.objects.filter(is_favorited))

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def get_shop_cart(self, query, name, value):
        user = self.request.user
        if self.request and value:
            return Recipe.objects.filter(author__author=user)
        return Recipe.objects.all()