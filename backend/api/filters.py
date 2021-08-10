import django_filters as filters

from api.models import Recipe

FILTER_CHOICES = (
    (0, 'True'),
    (1, 'False'),
)


class RecipeFilter(filters.FilterSet):
    """
    Перенесли фильтрацию во вьюсет, оставив только тэги

    """
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    # is_favorited = filters.BooleanFilter()


    class Meta:
        model = Recipe
        fields = ['author', 'tags',]

