from django.shortcuts import get_object_or_404
from django.views import View
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (Favorite, Follow, Ingredient, Recipe, ShoppingCart, Tag,
                     User)
from .serializers import (IngredientSerializer, ProfileSerializer,
                          RecipeSerializer, TagSerializer,
                          ShoppingCartSerializer, FavoriteSerializer)


class ProfileViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = (filters.SearchFilter,)

    @action(detail=False,
            methods=['get', 'patch'],
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        if request.method == 'GET':
            profile = get_object_or_404(User, username=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = ProfileSerializer(request.user,
                                       data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated))
    def shopping_cart(self, request):
        profile = request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        if request.method == 'POST':
            if ShoppingCart.objects.get(user=profile, recipe=recipe):
                Response('Вы уже добавляли этот рецепт',
                         status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=profile, recipe=recipe)
            serializer = ShoppingCartSerializer(recipe)
            Response(serializer.data, status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            ShoppingCart.objects.delete(profile, recipe)
            Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated))
    def favorite(self, request):
        profile = request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        if request.method == 'POST':
            if Favorite.objects.get(user=profile, recipe=recipe):
                Response('Вы уже добавляли этот рецепт',
                         status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=profile, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            Response(serializer.data, status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            ShoppingCart.objects.delete(profile, recipe)
            Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    pass
