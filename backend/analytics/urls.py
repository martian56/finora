from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'trading-stats', views.TradingStatsViewSet, basename='trading-stats')
router.register(r'portfolios', views.PortfolioViewSet, basename='portfolio')
router.register(r'trading-sessions', views.TradingSessionViewSet, basename='trading-session')
router.register(r'market-analytics', views.MarketAnalyticsViewSet, basename='market-analytics')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
