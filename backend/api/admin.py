from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    fields = (('author', 'name'), 'image', 'text', ('ingredients', 'tags'),
              'cooking_time')
    list_display = ('author', 'name', 'favorites_count')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author', 'name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('ingredient',)


admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
