from rest_framework import serializers

from api.models import (FavorRecipes, Follow, Ingredient, Recipe,
                        RecipeComponent, ShoppingList, Tag, User)
from users.serializers import AuthorSerializer


class FavorSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavorRecipes
        fiels = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


# Всё же его необходимо разбить - создавать универсальные,
# но монструозные сущности здесь неуместно
class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
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
                author=user, recipe=recipe
            ).exists()

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        user = request.user
        if request is None or user.is_anonymous:
            return False
        else:
            return FavorRecipes.objects.filter(
                author=user, recipes=recipe
            ).exists()


class IngredientInRecipe(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeComponent
        fields = ('id', 'amount')


class NewRecipeSerializer(serializers.ModelSerializer):
    """
    Выделили сериализатор, обрабатывающий процесс создания (и обновления)
    рецепта
    """
    author = AuthorSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientInRecipe(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text','author', 'author', 'tags', 'ingredients', 'cooking_time')

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author_id=author.id, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingr_inst = Ingredient.objects.get(id=ingredient['id'])
            amount = ingredient['amount']
            RecipeComponent.objects.create(
                ingredient=ingr_inst,
                recipe=recipe,
                amount=amount
            )
        return recipe


class FollowSerializer(serializers.ModelSerializer):
    results = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    # recipes = RecipeSerializer()

    class Meta:
        model = Follow
        fields = '__all__'


class ListFollowSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(method_name='get_rec_count')
    is_subscribed = serializers.SerializerMethodField(method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, user):
        rq_user = self.context.get('current_user')
        author_follows = user.following.all()
        if user.is_anonymous or author_follows.count() == 0:
            return False
        elif Follow.objects.filter(user=user, author=rq_user).exists():
            return True


class ShoppingSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = ShoppingList
        fields = '__all__'

class ListFavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
