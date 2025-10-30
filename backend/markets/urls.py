from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'currencies', views.CurrencyViewSet)
router.register(r'trading-pairs', views.TradingPairViewSet)
router.register(r'market-data', views.MarketDataViewSet)
router.register(r'price-history', views.PriceHistoryViewSet)

urlpatterns = [
    # Market data endpoints
    path('tickers/', views.TickerListView.as_view(), name='tickers'),
    path('ticker/<path:symbol>/', views.TickerDetailView.as_view(), name='ticker_detail'),
    path('orderbook/<path:symbol>/', views.OrderBookView.as_view(), name='orderbook'),
    path('klines/<path:symbol>/', views.KlinesView.as_view(), name='klines'),
    
    # Include router URLs
    path('', include(router.urls)),
]
