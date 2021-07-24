from django.db import models

from users.models import User



class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    units = models.CharField(
        max_length=16
    )

    class Meta:
        verbose_name = 'Ingredient'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Тэг'
    )
    color = models.CharField(
        max_length=200,
        verbose_name='Smh',
        null=True
    )
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='media/',
        blank=True, null=True,
        verbose_name='Картинка рецепта'
    )  # Add upload_to, verb name
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ingredients',
        through='RecipeComponent'
    )
    text = models.TextField(
        max_length=255,
        null=True
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Tags'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Рецепт'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name[:32]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчики'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписки'
    )

    class Meta:
        unique_together = ['user', 'author']


class ShoppingList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shop_list'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='author'
    )


class FavorRecipes(models.Model):
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Любимые рецепты',
        related_name='favorite_recipes',
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorites',
        verbose_name='Пользователь'
    )

    class Meta:
        unique_together = ['recipes', 'author']


class RecipeComponent(models.Model):
    """
    Класс, описывающий ингридиенты как часть рецепта
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Компонент рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='component_recipes',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField()
