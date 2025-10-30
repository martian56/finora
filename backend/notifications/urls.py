from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.NotificationViewSet, basename='notification')
router.register(r'price-alerts', views.PriceAlertViewSet, basename='price-alert')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
