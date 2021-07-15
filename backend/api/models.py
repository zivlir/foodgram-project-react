from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingridient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    units = models.CharField(
        max_length=16
    )

    class Meta:
        verbose_name = 'Ingridient'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Тэг'
    )
    color = models.CharField(
        max_length=200,
        verbose_name='Smh'
    )
    slug = models.SlugField(unique=True)

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
    ingridients = models.ManyToManyField(
        Ingridient,
        verbose_name='Ingridients',
        through='RecipeComponent'
    )
    description = models.TextField(
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


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписичник'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        unique_together = ['user', 'following']


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
        related_name='favorite',
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )

    class Meta:
        unique_together = ['recipes', 'author']


class RecipeComponent(models.Model):
    """
    Класс, описывающий ингридиенты как часть рецепта
    """
    ingridient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        related_name='recipe_ingridient',
        verbose_name='Компонент рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='component_recipes',
        verbose_name='Рецепт'
    )
    ingridients_amt = models.PositiveSmallIntegerField()
