from django.core.management.base import BaseCommand
from markets.models import TradingPair, MarketData
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Generate initial market data for all active trading pairs'

    def handle(self, *args, **options):
        trading_pairs = TradingPair.objects.filter(status='active')
        
        if not trading_pairs.exists():
            self.stdout.write(self.style.ERROR('No active trading pairs found'))
            return
        
        for pair in trading_pairs:
            # Check if market data already exists
            existing = MarketData.objects.filter(trading_pair=pair).first()
            
            if existing:
                self.stdout.write(
                    self.style.WARNING(f'Market data already exists for {pair.symbol}')
                )
                continue
            
            # Generate realistic initial prices based on common crypto prices
            if 'BTC' in pair.symbol:
                base_price = Decimal('50000.00')
            elif 'ETH' in pair.symbol:
                base_price = Decimal('3000.00')
            elif 'BNB' in pair.symbol:
                base_price = Decimal('400.00')
            elif 'SOL' in pair.symbol:
                base_price = Decimal('100.00')
            else:
                base_price = Decimal('1.00')
            
            # Add some randomness
            price_variation = Decimal(str(random.uniform(-0.05, 0.05)))
            price = base_price * (Decimal('1') + price_variation)
            
            # Generate 24h data
            high_24h = price * Decimal('1.02')
            low_24h = price * Decimal('0.98')
            volume_24h = Decimal(str(random.uniform(1000, 10000)))
            change_24h = Decimal(str(random.uniform(-5, 5)))
            change_percent_24h = Decimal(str(random.uniform(-5, 5)))
            
            # Create market data
            MarketData.objects.create(
                trading_pair=pair,
                price=price,
                volume_24h=volume_24h,
                change_24h=change_24h,
                change_percent_24h=change_percent_24h,
                high_24h=high_24h,
                low_24h=low_24h
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created market data for {pair.symbol} at ${price:.2f}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully generated market data for {trading_pairs.count()} trading pairs'
            )
        )

