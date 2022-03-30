from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import Ingredient, Recipe, Tag, User, Follow


class ProfileSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        if request.user.is_anonymous:
            return False
        else:
            return request.user.follower.filter(author=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    tegs = TagSerializer(many=True)
    ingredients = IngredientSerializer()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request.user.favorite.filter(recipe=obj.id).exist():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.customer.filter(recipe=obj.id).exist():
            return True
        return False


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    recipes = serializers.SerializerMethodField()


    class Meta:
        model = Follow
        fields = ('')

    def get_recipes(self, obj):
        pass
        #request = self.context.get('request')
