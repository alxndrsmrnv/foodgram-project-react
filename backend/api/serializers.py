from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Follow, Ingredient, IngredientAmount, Recipe, Tag, User


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
        if request is None or request.user.is_anonymous:
            return False
        else:
            return obj.follower.filter(author=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeRepresentation(serializers.ModelSerializer):

    class Meta:
        model = IngredientAmount
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        data = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(data, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.is_favorited.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.in_shopping_cart.filter(user=user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = ProfileSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, attrs):
        if len(attrs['ingredients']) == 0:
            raise ValidationError('В рецепте нет игредиентов')
        ingredients_id = []
        for ingredient in attrs['ingredients']:
            if ingredient['amount'] <= 0:
                raise ValidationError('Кольчество не может быть меньше 0')
            ingredients_id.append(ingredient['ingredient']['id'])
        if len(ingredients_id) > len(set(ingredients_id)):
            raise ValidationError('Ингредиенты не могут повторяться')
        if attrs['cooking_time'] <= 0:
            raise ValidationError('Время приготовления не может быть меньше 0')
        if len(attrs['tags']) < 0:
            raise ValidationError('Добавьте теги')
        if len(attrs['tags']) > len(set(attrs['tags'])):
            raise ValidationError('Ингредиенты не могут повторяться')
        return attrs

    def set_tags_ingredients(self, obj, tags, ingredients):
        obj.tags.set(tags)
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=obj,
                ingredient=get_object_or_404(Ingredient,
                                             id=ingredient['ingredient']['id']
                                             ),
                amount=ingredient.get('amount')
            )
        return obj

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(
            image=image,
            author=author,
            **validated_data
        )
        self.set_tags_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):  # вроде все правильно работает
        instance.tags.clear()  # Да они очищаются, но не удаляются из базы
        instance.ingredients.clear()
        tags = validated_data.pop('tags')  # модель ингредиента если так не
        ingredients = validated_data.pop('ingredients')  # делать, то связка
        super().update(instance, validated_data)
        IngredientAmount.objects.filter(recipe=instance).delete()  # <- это не
        self.set_tags_ingredients(instance, tags, ingredients)  # останется в
        return instance  # базе, это удаление связки.

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}).data


class RecipeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        else:
            return obj.follower.filter(author=obj.id).exists()

    def get_recipes(self, obj):
        recipes = obj.recipe.all()
        request = self.context.get('request')
        context = {'request': request}
        return RecipeInfoSerializer(recipes, many=True, context=context).data

    def get_recipes_count(self, obj):
        return obj.recipe.count()


class FollowUnfollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('user', 'author')
