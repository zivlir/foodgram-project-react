from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from api.models import (FavorRecipes, Follow, Ingredient, Recipe,
                        RecipeComponent, ShoppingList, Tag)
from users.models import User
from users.serializers import UserSerializer

class FollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('user', 'author')


    def validate(self, data):
        user = self.context.get('request').user
        author_id = data['author'].id
        follow_exist = Follow.objects.filter(
            user=user,
            author__id=author_id
        ).exists()

        if self.context.get('request').method == 'GET':
            if user.id == author_id or follow_exist:
                raise serializers.ValidationError(
                    'Подписка существует')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowReadSerializer(
            instance.author,
            context=context).data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeUserWriteSerializer(serializers.ModelSerializer):
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



class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для валидации создания и обновления рецептов
    """
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        slug_field='id'
    )
    cooking_time = serializers.IntegerField()
    ingredients = IngredientWriteSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate(self, attrs):
        ingredients = self.initial_data.get('ingredients')
        if ingredients.count() == 0:
            raise serializers.ValidationError(
                {'ingredients': (
                    'Список ингридиентов не получен'
                )}
            )
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    {'ingredients': (
                        'Поле amount не может быть отрицательным!')
                    }
                )
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.save()
        recipe.tags.set(tags)
        ingr_inst = []
        # recipe.ingredients.bulk_create(ingredients)
        for ingredient in ingredients:
            ingr_id = Ingredient.objects.get(id=ingredient['id'])
            amt = ingredient['amount']
            RecipeComponent.objects.create(
                ingredient=ingr_id,
                recipe=recipe,
                amount=amt
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

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField('get_ingredients')
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('__all__')

    def get_ingredients(self, recipe):
        queryset = RecipeComponent.objects.filter(recipe=recipe)
        return RecipeComponentSerializer(queryset, many=True).data

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





class FollowReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = RecipeReadSerializer(many=True, read_only=True)
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
        if Follow.objects.filter(user=user, author=author).exists():
            return True
        return False


class FollowerReadSerializer(serializers.ModelSerializer):
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
    recipes = FollowerReadSerializer(many=True, read_only=True)
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
    def validate(self, attrs):
        follow_exists = FavorRecipes.objects.filter(
            author=attrs['author'],
            recipes=attrs['recipes']
        ).exists()
        if follow_exists:
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в избранное'
            )
        return attrs

    class Meta:
        model = FavorRecipes
        fields = '__all__'


class ListFavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
