"""
Management command to generate and broadcast real-time market data.
"""
import asyncio
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from markets.models import TradingPair, MarketData


class Command(BaseCommand):
    help = 'Generate and broadcast real-time market data for all active trading pairs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=float,
            default=5.0,
            help='Update interval in seconds (default: 5.0)',
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit (initialize data)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options['once']
        
        if run_once:
            self.stdout.write(self.style.SUCCESS('Initializing market data (one-time)...'))
            self.initialize_market_data()
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Starting real-time market data generator (interval: {interval}s)'
            ))
            self.run_continuous(interval)

    def initialize_market_data(self):
        """Initialize market data for trading pairs that don't have any."""
        trading_pairs = TradingPair.objects.filter(status='active')
        
        if not trading_pairs.exists():
            self.stdout.write(self.style.ERROR('No active trading pairs found'))
            return
        
        created_count = 0
        for pair in trading_pairs:
            # Check if market data already exists
            existing = MarketData.objects.filter(trading_pair=pair).first()
            
            if existing:
                self.stdout.write(
                    self.style.WARNING(f'Market data already exists for {pair.symbol}')
                )
                continue
            
            # Generate initial market data
            market_data = self.generate_market_data_for_pair(pair, is_initial=True)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created market data for {pair.symbol} at ${market_data["price"]:.2f}'
                )
            )
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully initialized market data for {created_count} trading pairs'
            )
        )

    def run_continuous(self, interval):
        """Continuously update and broadcast market data."""
        channel_layer = get_channel_layer()
        
        try:
            while True:
                # Get all active trading pairs
                trading_pairs = TradingPair.objects.filter(status='active')
                
                for pair in trading_pairs:
                    # Get or create market data
                    market_data_obj = MarketData.objects.filter(trading_pair=pair).first()
                    
                    if not market_data_obj:
                        # Initialize if doesn't exist
                        data = self.generate_market_data_for_pair(pair, is_initial=True)
                        self.stdout.write(
                            self.style.SUCCESS(f'Initialized {pair.symbol} at ${data["price"]:.2f}')
                        )
                    else:
                        # Update existing data
                        data = self.generate_market_data_for_pair(pair, is_initial=False, current_price=market_data_obj.price)
                        
                        # Update database
                        market_data_obj.price = Decimal(str(data['price']))
                        market_data_obj.volume_24h = Decimal(str(data['volume_24h']))
                        market_data_obj.change_24h = Decimal(str(data['change_24h']))
                        market_data_obj.change_percent_24h = Decimal(str(data['change_percent_24h']))
                        market_data_obj.high_24h = Decimal(str(data['high_24h']))
                        market_data_obj.low_24h = Decimal(str(data['low_24h']))
                        market_data_obj.save()
                        
                        # Broadcast to WebSocket
                        # Sanitize trading pair symbol for group name (replace / with -)
                        sanitized_symbol = pair.symbol.replace('/', '-')
                        group_name = f'price_{sanitized_symbol}'
                        
                        async_to_sync(channel_layer.group_send)(
                            group_name,
                            {
                                'type': 'price_update',
                                'data': data
                            }
                        )
                        
                        self.stdout.write(
                            f'Updated {pair.symbol}: ${data["price"]:.2f} '
                            f'({data["change_percent_24h"]:+.2f}%) '
                            f'Vol: {data["volume_24h"]:.2f}'
                        )
                
                # Wait before next update
                asyncio.run(asyncio.sleep(interval))
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping market data generator...'))

    def generate_market_data_for_pair(self, pair, is_initial=False, current_price=None):
        """Generate market data for a trading pair."""
        if is_initial:
            # Generate initial price based on common crypto prices
            if 'BTC' in pair.symbol:
                base_price = 50000.00
            elif 'ETH' in pair.symbol:
                base_price = 3000.00
            elif 'BNB' in pair.symbol:
                base_price = 400.00
            elif 'SOL' in pair.symbol:
                base_price = 100.00
            else:
                base_price = 1.00
            
            # Add some randomness
            price_variation = random.uniform(-0.05, 0.05)
            price = base_price * (1 + price_variation)
            
            # Generate 24h data
            high_24h = price * 1.02
            low_24h = price * 0.98
            volume_24h = random.uniform(1000, 10000)
            change_24h = random.uniform(-5, 5)
            change_percent_24h = random.uniform(-5, 5)
            
            # Create in database
            MarketData.objects.create(
                trading_pair=pair,
                price=Decimal(str(price)),
                volume_24h=Decimal(str(volume_24h)),
                change_24h=Decimal(str(change_24h)),
                change_percent_24h=Decimal(str(change_percent_24h)),
                high_24h=Decimal(str(high_24h)),
                low_24h=Decimal(str(low_24h))
            )
        else:
            # Update existing price with small variation
            current_price = float(current_price)
            price_change = current_price * random.uniform(-0.001, 0.001)  # ±0.1% change
            price = current_price + price_change
            
            # Update 24h metrics
            high_24h = price * 1.02
            low_24h = price * 0.98
            volume_24h = random.uniform(1000, 10000)
            change_24h = price_change
            change_percent_24h = (price_change / current_price) * 100
        
        return {
            'price': price,
            'change_24h': change_24h,
            'change_percent_24h': change_percent_24h,
            'volume_24h': volume_24h,
            'high_24h': high_24h,
            'low_24h': low_24h,
            'timestamp': timezone.now().isoformat()
        }
