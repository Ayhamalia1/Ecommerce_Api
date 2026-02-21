from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewset, OrderViewset ,CategoryViewset,CartViewSet

router = DefaultRouter()
router.register('products', ProductViewset, basename='products')
router.register('orders', OrderViewset, basename='orders')
router.register('categories', CategoryViewset ,basename='categories')
router.register('cart',CartViewSet, basename='cart')








urlpatterns = [
    
    path('', include(router.urls)),
]