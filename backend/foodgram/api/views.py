import io

from django.db import IntegrityError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (Favorite, Follow, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag, User)
from .serializers import (FollowUnfollowSerializer, IngredientSerializer,
                          ProfileSerializer, RecipeCreateSerializer,
                          RecipeInfoSerializer, RecipeSerializer,
                          SubscribersSerializer, TagSerializer)


class ProfileViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = (filters.SearchFilter,)

    @action(detail=False,
            methods=('get',))
    def me(self, request):
        serializer = ProfileSerializer(request.user,
                                       data=request.data,
                                       partial=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscribersSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class FollowUnfollowViewSet(APIView):
    queryset = Follow.objects.all()
    serializer_class = FollowUnfollowSerializer

    def post(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if request.user == author:
            return Response('Вы не можете подписаться на себя',
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            Follow.objects.create(user=request.user, author=author)
            serializer = SubscribersSerializer(author)
            return Response(serializer.data, status.HTTP_201_CREATED)
        except IntegrityError:
            return Response('Вы уже подписаны на этого пользователя',
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        try:
            object = Follow.objects.get(author=author)
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response('Вы не подписаны на этого пользователя',
                            status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method == 'GET' or 'PATCH':
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=RecipeInfoSerializer,)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            try:
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeInfoSerializer(recipe)
                return Response(serializer.data, status.HTTP_201_CREATED)
            except IntegrityError:
                return Response('Уже в корзине',
                                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            try:
                object = ShoppingCart.objects.get(recipe=recipe)
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception:
                return Response('Нет в корзине',
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=RecipeInfoSerializer,)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            try:
                Favorite.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeInfoSerializer(recipe)
                return Response(serializer.data,
                                status.HTTP_201_CREATED)
            except IntegrityError:
                return Response('Уже в избранном',
                                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            try:
                object = Favorite.objects.get(recipe=recipe)
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception:
                return Response('Рецепт не добавлен в избранное',
                                status=status.HTTP_400_BAD_REQUEST)


class DownloadShoppingCart(APIView):

    def get(self, request):
        def shopping_list_struct(unit, amount):
            return unit, amount

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        textob = c.beginText()
        textob.setTextOrigin(inch, inch)
        pdfmetrics.registerFont(TTFont(
            'FreeSans',
            'c:/Dev/foodgram-project-react/data/FreeSans.ttf'))
        textob.setFont('FreeSans', 32)
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        shopping_list_name = []
        shopping_list_amount = []
        for recipe in shopping_cart:
            ingredients = IngredientAmount.objects.filter(
                recipe=recipe.recipe)
            for ingredient in ingredients:
                if ingredient.ingredient.name not in shopping_list_name:
                    shopping_list_name.append(ingredient.ingredient.name)
                    shopping_list_amount.append(
                        list(shopping_list_struct(ingredient.ingredient.
                                                  measurement_unit,
                                                  ingredient.amount)))
                else:
                    shopping_list_amount[shopping_list_name.index(
                        ingredient.ingredient.name
                    )][1] += ingredient.amount
        for index in range(len(shopping_list_name)):
            textob.textLine(
                f'{shopping_list_name[index].capitalize()}'
                f'({shopping_list_amount[index][0]})'
                f' - {shopping_list_amount[index][1]}')
        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)
        return FileResponse(buf, as_attachment=True,
                            filename='shopping_list.pdf')
