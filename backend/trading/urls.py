from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'trades', views.TradeViewSet, basename='trade')
router.register(r'futures-positions', views.FuturesPositionViewSet, basename='futures-position')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
