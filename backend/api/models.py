from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


tags = [
    ('Завтрак', 'Завтрак'),
    ('Обед', 'Обед'),
    ('Ужин', 'Ужин'),
]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='Имя')
    measurement_unit = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='Единица измерения')

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=10,
        choices=tags,
        verbose_name='Название')
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет')
    slug = models.SlugField(
        unique=True,
        default='')

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        blank=False,
        verbose_name='Автор')
    name = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        verbose_name='Картинка')
    text = models.TextField(
        blank=False,
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        blank=False)

    class Meta:
        ordering = ('-id',)

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
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite_recipe'
            )
        ]
