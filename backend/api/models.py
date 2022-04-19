from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Имя')
    measurement_unit = models.CharField(
        max_length=255,
        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингрединт'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=10,
        verbose_name='Название')
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет')
    slug = models.SlugField(
        unique=True,
        default='',
        verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор')
    name = models.CharField(
        max_length=255,
        verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка')
    text = models.TextField(
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name

    def favorites_count(self):
        return Favorite.objects.filter(recipe=self.id).count()


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиенты')
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиет и количество в рецепте'
        verbose_name_plural = 'Ингредиенты и количество в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_in_ingredient'
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_author_user_following'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name='Покупатель')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт в корзине')

    class Meta:
        verbose_name = 'Список рецептов'
        verbose_name_plural = 'Списки рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',), name='unique_recipe_shopping_cart'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        related_name='is_favorited',
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Список избранных'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite_recipe'
            )
        ]
