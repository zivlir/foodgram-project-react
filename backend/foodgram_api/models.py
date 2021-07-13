from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ingridient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    units = models.CharField(
        max_length=200
    )

    class Meta:
        verbose_name = "Ingridient"

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


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField()  # Add upload_to, verb name
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    ingridients = models.ManyToManyField(
        Ingridient,
        verbose_name='Ingridients'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='Tags'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time'
    )  # PSIF allows Ints up to 32 767 m (546 hours!)

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписичник'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

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
        verbose_name='Автор',
        related_name='author'
    )

class FavorRecipes(models.Model):
    favorites = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Любимые рецепт(ы)',  #?
        related_name='favorite_recipes'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_author',
        verbose_name='Пользователь'
    )