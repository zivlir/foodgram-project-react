from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.models import (FavorRecipes, Follow, Ingredient, Recipe,
                        RecipeComponent, ShoppingList, Tag, User)


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name')


class UserSerializerCom(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=author
        ).exists()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class ListRecipeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class RecipeComponentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    units = serializers.ReadOnlyField(
        source='ingredient.units'
    )

    class Meta:
        model = RecipeComponent
        fields = ('id', 'name', 'units', 'amount',)

# Всё же его необходимо разбить - создавать универсальные,
# но монструозные сущности здесь неуместно
class RecipeSerializer(serializers.ModelSerializer):
    """
    Модель для отображения рецептов
    """
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )
    image = serializers.ImageField(
        max_length=None,
        required=False,
        allow_empty_file=False,
        use_url=True,
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


class NewRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeComponentSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text','author',
            'tags', 'ingredients', 'cooking_time', 'image'
        )


    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingr_inst = Ingredient.objects.get(
                id=ingredient['ingredient']['id']
            )  #wtf?
            amount = ingredient['amount']
            RecipeComponent.objects.create(
                ingredient=ingr_inst,
                recipe=recipe,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeComponent.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            qs = Ingredient.objects.filter(id=ingredient['ingredient']['id'])
            RecipeComponent.objects.create(
                ingredient=qs.first(),
                recipe=instance,
                amount=ingredient['amount']
            )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        instance.tags.set(tags)
        return instance


class ListFollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, user):
        return user.recipes.count()

    def get_is_subscribed(self, user):
        author = self.context.get('current_user')
        author_follows = user.following.all()
        if user.is_anonymous or author_follows.count() == 0:
            return False
        elif Follow.objects.filter(user=user, author=author).exists():
            return True


class ListFollowerSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        max_length=None,
        required=True,
        allow_empty_file=False,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ListSubscriptionsSerializer(serializers.ModelSerializer):
    recipes = ListFollowerSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField('count_author_recipes')
    is_subscribed = serializers.SerializerMethodField('check_if_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def count_author_recipes(self, user):
        return len(user.recipes.all())

    def check_if_subscribed(self, user):
        current_user = self.context.get('current_user')
        other_user = user.following.all()
        if user.is_anonymous:
            return False
        if other_user.count() == 0:
            return False
        if Follow.objects.filter(user=user, author=current_user).exists():
            return True
        return False

class ShoppingSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = ShoppingList
        fields = '__all__'


class FavorSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavorRecipes
        fiels = ('id', 'name', 'image', 'cooking_time')


class ListFavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
