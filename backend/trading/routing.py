from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/trading/(?P<room_name>\w+)/$', consumers.TradingConsumer.as_asgi()),
    re_path(r'ws/orderbook/(?P<trading_pair>\w+)/$', consumers.OrderBookConsumer.as_asgi()),
    re_path(r'ws/price/(?P<trading_pair>\w+)/$', consumers.PriceConsumer.as_asgi()),
]
