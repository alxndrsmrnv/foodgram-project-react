from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCart, FollowUnfollowViewSet,
                    IngredientViewSet, ProfileViewSet, RecipeViewSet,
                    SubscribersViewSet, TagViewSet)

router = DefaultRouter()
router.register(r'users/subscriptions', SubscribersViewSet,
                basename='subscriptions')
router.register(r'users', ProfileViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('recipes/download_shopping_cart/',
         DownloadShoppingCart.as_view(), name='download_shopping_cart'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:author_id>/subscribe/',
         FollowUnfollowViewSet.as_view(),
         name='subscribe'),
]
