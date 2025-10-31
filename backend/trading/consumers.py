import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from markets.models import TradingPair, MarketData
from trading.models import OrderBook

User = get_user_model()


class TradingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time trading updates.
    """
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'trading_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'subscribe':
            trading_pair = text_data_json.get('trading_pair')
            await self.subscribe_to_trading_pair(trading_pair)
        elif message_type == 'unsubscribe':
            trading_pair = text_data_json.get('trading_pair')
            await self.unsubscribe_from_trading_pair(trading_pair)
    
    async def subscribe_to_trading_pair(self, trading_pair):
        """Subscribe to updates for a specific trading pair."""
        if trading_pair:
            group_name = f'trading_{trading_pair}'
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )
    
    async def unsubscribe_from_trading_pair(self, trading_pair):
        """Unsubscribe from updates for a specific trading pair."""
        if trading_pair:
            group_name = f'trading_{trading_pair}'
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )
    
    # Receive message from room group
    async def trading_update(self, event):
        """Send trading update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'trading_update',
            'data': event['data']
        }))


class OrderBookConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time order book updates.
    """
    async def connect(self):
        self.trading_pair = self.scope['url_route']['kwargs']['trading_pair']
        # Sanitize trading pair for use in group name (replace / with -)
        sanitized_pair = self.trading_pair.replace('/', '-')
        self.room_group_name = f'orderbook_{sanitized_pair}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial order book data
        await self.send_initial_orderbook()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def send_initial_orderbook(self):
        """Send initial order book data."""
        orderbook_data = await self.get_orderbook_data()
        await self.send(text_data=json.dumps({
            'type': 'orderbook_data',
            'data': orderbook_data
        }))
    
    @database_sync_to_async
    def get_orderbook_data(self):
        """Get order book data from database."""
        try:
            trading_pair = TradingPair.objects.get(symbol=self.trading_pair)
            
            # Get buy orders (bids)
            buy_orders = OrderBook.objects.filter(
                trading_pair=trading_pair,
                side='buy'
            ).order_by('-price')[:20]
            
            # Get sell orders (asks)
            sell_orders = OrderBook.objects.filter(
                trading_pair=trading_pair,
                side='sell'
            ).order_by('price')[:20]
            
            return {
                'bids': [
                    {
                        'price': float(order.price),
                        'quantity': float(order.quantity),
                        'count': order.order_count
                    }
                    for order in buy_orders
                ],
                'asks': [
                    {
                        'price': float(order.price),
                        'quantity': float(order.quantity),
                        'count': order.order_count
                    }
                    for order in sell_orders
                ]
            }
        except TradingPair.DoesNotExist:
            return {'bids': [], 'asks': []}
    
    # Receive message from room group
    async def orderbook_update(self, event):
        """Send order book update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'orderbook_update',
            'data': event['data']
        }))


class PriceConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time price updates.
    """
    async def connect(self):
        self.trading_pair = self.scope['url_route']['kwargs']['trading_pair']
        # Sanitize trading pair for use in group name (replace / with -)
        sanitized_pair = self.trading_pair.replace('/', '-')
        self.room_group_name = f'price_{sanitized_pair}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial price data
        await self.send_initial_price()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def send_initial_price(self):
        """Send initial price data."""
        price_data = await self.get_price_data()
        await self.send(text_data=json.dumps({
            'type': 'price_data',
            'data': price_data
        }))
    
    @database_sync_to_async
    def get_price_data(self):
        """Get current price data from database."""
        try:
            trading_pair = TradingPair.objects.get(symbol=self.trading_pair)
            market_data = MarketData.objects.filter(
                trading_pair=trading_pair
            ).order_by('-timestamp').first()
            
            if market_data:
                return {
                    'price': float(market_data.price),
                    'change_24h': float(market_data.change_24h),
                    'change_percent_24h': float(market_data.change_percent_24h),
                    'volume_24h': float(market_data.volume_24h),
                    'high_24h': float(market_data.high_24h),
                    'low_24h': float(market_data.low_24h),
                    'timestamp': market_data.timestamp.isoformat()
                }
            return {}
        except TradingPair.DoesNotExist:
            return {}
    
    # Receive message from room group
    async def price_update(self, event):
        """Send price update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'price_update',
            'data': event['data']
        }))


class KlineConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time candlestick/kline updates.
    """
    async def connect(self):
        self.trading_pair = self.scope['url_route']['kwargs']['trading_pair']
        self.interval = self.scope['url_route']['kwargs']['interval']
        # Sanitize trading pair for use in group name (replace / with -)
        sanitized_pair = self.trading_pair.replace('/', '-')
        self.room_group_name = f'klines_{sanitized_pair}_{self.interval}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial kline data
        await self.send_initial_klines()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def send_initial_klines(self):
        """Send initial kline data."""
        kline_data = await self.get_kline_data()
        await self.send(text_data=json.dumps({
            'type': 'kline_data',
            'data': kline_data
        }))
    
    @database_sync_to_async
    def get_kline_data(self):
        """Get kline data from database."""
        # For now, return empty data as we don't have historical kline storage yet
        # This would typically fetch from a PriceHistory or Kline model
        return []
    
    # Receive message from room group
    async def kline_update(self, event):
        """Send kline update to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'kline_update',
            'data': event['data']
        }))
    
    async def kline_data(self, event):
        """Send kline data to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'kline_data',
            'data': event['data']
        }))

