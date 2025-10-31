"""
Management command to generate and broadcast real-time order book data.
"""
import asyncio
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from markets.models import TradingPair, MarketData
from trading.models import OrderBook


class Command(BaseCommand):
    help = 'Generate and broadcast real-time order book data for all active trading pairs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=float,
            default=2.0,
            help='Update interval in seconds (default: 2.0)',
        )
        parser.add_argument(
            '--depth',
            type=int,
            default=15,
            help='Order book depth (default: 15 levels)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        depth = options['depth']
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting order book generator (interval: {interval}s, depth: {depth})'
        ))
        
        channel_layer = get_channel_layer()
        
        try:
            while True:
                # Get all active trading pairs
                trading_pairs = TradingPair.objects.filter(status='active')
                
                for pair in trading_pairs:
                    # Get or generate base price
                    market_data = MarketData.objects.filter(
                        trading_pair=pair
                    ).order_by('-timestamp').first()
                    
                    if market_data:
                        base_price = float(market_data.price)
                    else:
                        # Use a default price if no market data exists
                        base_price = 50000.0 if 'BTC' in pair.symbol else 1.0
                    
                    # Generate order book data
                    orderbook_data = self.generate_orderbook(base_price, depth)
                    
                    # Update database
                    self.update_orderbook_db(pair, orderbook_data)
                    
                    # Broadcast to WebSocket
                    # Sanitize trading pair symbol for group name (replace / with -)
                    sanitized_symbol = pair.symbol.replace('/', '-')
                    group_name = f'orderbook_{sanitized_symbol}'
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            'type': 'orderbook_update',
                            'data': orderbook_data
                        }
                    )
                    
                    self.stdout.write(
                        f'Updated order book for {pair.symbol} - '
                        f'Bids: {len(orderbook_data["bids"])}, '
                        f'Asks: {len(orderbook_data["asks"])}'
                    )
                
                # Wait before next update
                asyncio.run(asyncio.sleep(interval))
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping order book generator...'))

    def generate_orderbook(self, base_price, depth):
        """Generate realistic order book data."""
        bids = []
        asks = []
        
        # Generate bids (buy orders) - prices below base price
        for i in range(depth):
            price_offset = (i + 1) * (base_price * random.uniform(0.0001, 0.0005))
            price = base_price - price_offset
            quantity = random.uniform(0.1, 5.0)
            total = price * quantity
            
            bids.append({
                'price': round(price, 2),
                'quantity': round(quantity, 6),
                'total': round(total, 2),
                'count': random.randint(1, 10)
            })
        
        # Generate asks (sell orders) - prices above base price
        for i in range(depth):
            price_offset = (i + 1) * (base_price * random.uniform(0.0001, 0.0005))
            price = base_price + price_offset
            quantity = random.uniform(0.1, 5.0)
            total = price * quantity
            
            asks.append({
                'price': round(price, 2),
                'quantity': round(quantity, 6),
                'total': round(total, 2),
                'count': random.randint(1, 10)
            })
        
        return {
            'bids': bids,
            'asks': asks,
            'timestamp': timezone.now().isoformat()
        }

    def update_orderbook_db(self, trading_pair, orderbook_data):
        """Update order book in database."""
        # Get existing prices to track which ones to keep
        existing_bids = set()
        existing_asks = set()
        
        # Update or create bid entries
        for bid in orderbook_data['bids'][:10]:  # Store top 10
            price = Decimal(str(bid['price']))
            existing_bids.add(price)
            
            OrderBook.objects.update_or_create(
                trading_pair=trading_pair,
                side='buy',
                price=price,
                defaults={
                    'quantity': Decimal(str(bid['quantity'])),
                    'order_count': bid['count']
                }
            )
        
        # Update or create ask entries
        for ask in orderbook_data['asks'][:10]:  # Store top 10
            price = Decimal(str(ask['price']))
            existing_asks.add(price)
            
            OrderBook.objects.update_or_create(
                trading_pair=trading_pair,
                side='sell',
                price=price,
                defaults={
                    'quantity': Decimal(str(ask['quantity'])),
                    'order_count': ask['count']
                }
            )
        
        # Clean up old entries that are no longer in the order book
        OrderBook.objects.filter(
            trading_pair=trading_pair,
            side='buy'
        ).exclude(price__in=existing_bids).delete()
        
        OrderBook.objects.filter(
            trading_pair=trading_pair,
            side='sell'
        ).exclude(price__in=existing_asks).delete()


