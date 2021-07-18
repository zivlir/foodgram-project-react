import django_filters

from api.models import Recipe, FavorRecipes, Tag

class RecipeFilter(django_filters.FilterSet):
    class Meta:
        model = Recipe
