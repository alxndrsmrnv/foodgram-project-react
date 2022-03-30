from django.contrib import admin

from .models import Favorite, Follow, Ingredient, Recipe, ShoppingCart, Tag


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'image', 'text', 'cooking_time')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
