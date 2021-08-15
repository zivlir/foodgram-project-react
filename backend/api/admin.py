from django.contrib import admin

from api.models import (FavorRecipes, Follow, Ingredient, Recipe,
                        RecipeComponent, Tag, User)


class RecipeComponentAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 2


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeComponentAdmin,)
    list_display = ('pk', 'name', 'author')
    list_display_links = ('name', )
    search_fields = ('author', 'name')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', )


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'units')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')


class FavorAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipes')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngridientAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(FavorRecipes, FavorAdmin)
