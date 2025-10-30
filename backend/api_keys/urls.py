from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.APIKeyViewSet, basename='apikey')
router.register(r'usage', views.APIKeyUsageViewSet, basename='apikey-usage')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
