from django.db import models
from django.db.models import Exists, OuterRef, Value
from django.core.exceptions import ValidationError
from users.models import User

class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    units = models.CharField(
        max_length=16,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингидиент'
        verbose_name_plural = 'Ингидиенты'

    def __str__(self):
        return f'{self.name}, {self.units}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Тэг'
    )
    color = models.CharField(
        max_length=200,
        verbose_name='Цвет',
        null=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Короткое имя'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.slug


class RecipeQuerySet(models.QuerySet):
    """
    Выделенный QS с дополнительными аннотированными полями
    """
    def opt_annotations(self, user):
        if user.is_anonymous:
            return self.annotate(
                is_favorited=Value(
                    False, output_field=models.BooleanField()
                ),
                is_in_shopping_cart=Value(
                    False, output_field=models.BooleanField()
                )
            )
        return self.annotate(
            is_favorited=Exists(FavorRecipes.objects.filter(
                author=user, recipes_id=OuterRef('pk')
            )),
            is_in_shopping_list=Exists(ShoppingList.objects.filter(
                author=user, recipe_id=OuterRef('pk')
            ))
        )


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='media/',
        blank=True, null=True,
        verbose_name='Картинка рецепта'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингидиенты',
        through='RecipeComponent'
    )
    text = models.TextField(
        max_length=255,
        null=True
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def clean(self):
        if self.ingredients.count() < 1:
            raise ValidationError('Список ингридиентов не может быть пуст!')
        if self.cooking_time < 1:
            raise ValidationError(
                'Время приготовления - неотрицательное значение'
            )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
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
    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Нельзя подписаться на самого себя'
            )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Список избранного'
        unique_together = ['user', 'author']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow_user_author_unique'
            )
        ]


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

    class Meta:
        verbose_name='Рецепт в корзине'
        verbose_name_plural='Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='shopping_author_recipe_unique'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.author}'



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
        constraints = [
            models.UniqueConstraint(
                name='favorite_author_unique_recipes',
                fields=['author', 'recipes']
            )
        ]


class RecipeComponent(models.Model):
    """
    Класс, описывающий ингридиенты как часть рецепта
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Ингидиенты'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='component_recipes',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингидиента'
        constraints = [
            models.UniqueConstraint(
                name='recipe_unique_component',
                fields=['ingredient', 'recipe']
            )
        ]
