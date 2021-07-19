from rest_framework import serializers

from api.models import (FavorRecipes, Follow, Ingridient, Recipe,
                        RecipeComponent, ShoppingList, Tag, User)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class FavorSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavorRecipes
        fiels = '__all__'


# Всё же его необходимо разбить - создавать универсальные,
# но монструозные сущности здесь неуместно
class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='slug'
    )
    author = AuthorSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    class Meta:
        fields = '__all__'
        model = Recipe

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        user = request.user
        if request is None or user.is_anonymous:
            return False
        else:
            return ShoppingList.objects.filter(
                user=user, recipe=recipe
            ).exists()

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        user = request.user
        if request is None or user.is_anonymous:
            return False
        else:
            return FavorRecipes.objects.filter(author=user, recipes=recipe).exists()

class NewRecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='slug'
    )

    def create(self, validated_data):
        author = self.context.get('request').user
        if author is None or author.is_anonymous:
            return False


class FollowSerializer(serializers.ModelSerializer):
    results = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipes = RecipeSerializer()

    class Meta:
        model = Follow
        fields = '__all__'


class IngidientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        fields = '__all__'


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
