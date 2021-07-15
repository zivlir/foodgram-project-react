from django.contrib import admin

from api.models import FavorRecipes, Follow, Ingridient, Recipe, Tag, User, RecipeComponent


class RecipeComponentAdmin(admin.TabularInline):
    model = Recipe.ingridients.through
    extra = 2

class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeComponentAdmin,)
    list_display = ('pk', 'name', 'author')
    search_fields = ('author', '')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', )


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'units')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')


class FavorAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipes')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(FavorRecipes, FavorAdmin)
