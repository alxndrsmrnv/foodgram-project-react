from django.contrib.auth import get_user_model
from django.db import models
from django.utils.html import format_html

User = get_user_model()


tags = [
    ('breakfast', 'Завтрак'),
    ('lunch', 'Обед'),
    ('dinner', 'Ужин'),
]


class Ingredient(models.Model):
    name = models.CharField(max_length=255, blank=False)
    measurement_unit = models.CharField(max_length=255, blank=False)


class Tag(models.Model):
    name = models.CharField(max_length=10, choices=tags)
    color = models.CharField(max_length=7)
    slug = models.SlugField(unique=True, default='')

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.title,
            self.hex,
            self.slug,
        )


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipe', blank=False)
    name = models.CharField(max_length=255, blank=False)
    image = models.ImageField(upload_to='recipes/', blank=False)
    text = models.TextField(blank=False)
    ingredients = models.ManyToManyField(Ingredient, blank=False)
    tegs = models.ManyToManyField(Tag, blank=False)
    cooking_time = models.TimeField(blank=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self) -> str:
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_author_user_following'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='customer')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_shopping_cart')
    amount = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_recipe_shopping_cart'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorite',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='is_favorite',
                               on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite_recipe'
            )
        ]
