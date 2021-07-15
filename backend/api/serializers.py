from rest_framework import serializers

from api.models import Ingridient, Recipe, RecipeComponent


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Recipe
