import io

from django.db import IntegrityError
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Follow, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag, User)
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (FollowUnfollowSerializer, IngredientSerializer,
                          ProfileSerializer, RecipeCreateSerializer,
                          RecipeInfoSerializer, RecipeSerializer,
                          SubscribersSerializer, TagSerializer)


class ProfileViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (permissions.AllowAny,)

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
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class FollowUnfollowViewSet(APIView):
    queryset = Follow.objects.all()
    serializer_class = FollowUnfollowSerializer
    permission_classes = (permissions.IsAuthenticated,)

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
            object = Follow.objects.get(user=request.user, author=author)
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response('Вы не подписаны на этого пользователя',
                            status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        return super().perform_create(serializer)

    def favorite_and_shopping_cart(self, request, model, recipe):
        if request.method == 'POST':
            try:
                model.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeInfoSerializer(recipe)
                return Response(serializer.data,
                                status.HTTP_201_CREATED)
            except IntegrityError:
                return Response('Уже добавлено',
                                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            try:
                object = model.objects.get(user=request.user,
                                           recipe=recipe)
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except model.DoesNotExist:
                return Response('Не добавлено',
                                status=status.HTTP_400_BAD_REQUEST)
        return Response('Что-то пошло не так',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=RecipeInfoSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.favorite_and_shopping_cart(request, ShoppingCart, recipe)

    @action(detail=True,
            methods=('post', 'delete'),
            serializer_class=RecipeInfoSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.favorite_and_shopping_cart(request, Favorite, recipe)


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
            'FreeSans.ttf'))
        textob.setFont('FreeSans', 15)
        shopping_cart = ShoppingCart.objects.filter(user=request.user).values()
        shopping_list_name = []
        shopping_list_amount = []
        ingredients = Recipe.objects.filter(
            in_shopping_cart__user=request.user).values(
                'ingredients__name',
                'ingredients__measurement_unit',
                'ingredientamount__amount'
                ).order_by(
            'ingredients__name').annotate(
                total_amount=Sum(
                    'ingredientamount__amount'))
        for recipe in shopping_cart:
            ingredient = IngredientAmount.objects.get(
                recipe=recipe['recipe_id'])
            if ingredient.ingredient.name not in shopping_list_name:
                shopping_list_name.append(ingredient.ingredient.name)
            shopping_list_amount.append(
                list(shopping_list_struct(ingredient.ingredient.
                                          measurement_unit,
                                          ingredient.amount)))
        index = 1
        for ingredient in ingredients:
            total = ingredient['total_amount']
            if index % 37 == 0:
                c.drawText(textob)
                c.showPage()
                textob = c.beginText()
                textob.setTextOrigin(inch, inch)
                textob.setFont('FreeSans', 15)
            textob.textLine(
                f'{shopping_list_name[index-1].capitalize()}'
                f'({shopping_list_amount[index-1][0]})'
                f' - {total}')
            index += 1
        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)
        return FileResponse(buf, as_attachment=True,
                            filename='shopping_list.pdf')
