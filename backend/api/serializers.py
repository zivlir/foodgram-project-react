from rest_framework import serializers

from api.models import Recipe, RecipeComponent, Ingridient

class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Recipe

