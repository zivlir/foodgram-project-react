from rest_framework import serializers

from api.models import Ingridient, Recipe, RecipeComponent, FavorRecipes, Tag, ShoppingList, User, Follow

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')



class UserFollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow

class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='slug'
    )
    # author = serializers.RelatedField(source='user', read_only=True)
    # ingridients = serializers.RelatedField(source='ingridient')

    class Meta:
        fields = '__all__'
        model = Recipe


class IngidientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        fields = '__all__'

class FavorSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavorRecipes
        fiels = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

class ShoppingSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = ShoppingList
        fields = '__all__'