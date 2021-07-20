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


class IngidientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
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
    """
    Выделили сериализатор, обрабатывающий процесс создания (и обновления)
    рецепта
    """
    author = AuthorSerializer
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='slug'
    )
    ingridients = serializers.PrimaryKeyRelatedField(
        queryset=Ingridient.objects.all()
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        author = self.context.get('request').user
        ingridients = validated_data.pop('ingridients')
        tags = validated_data.pop('tags')
        for tag in tags:
            Tag.objects.update_or_create(tag)
        recipe = Recipe.objects.create(author_id=author.id, **validated_data)
        for ingridient in ingridients:
            ingr_inst = ingridient['id']
            amout = ingridient['amount']
            RecipeComponent.objects.get_or_create(
                ingridient=ingr_inst,
                recipe=recipe,
                ingridients_amt=amout
            )
        return recipe


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


class ShoppingSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = ShoppingList
        fields = '__all__'
