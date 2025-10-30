from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Currency(models.Model):
    """
    Represents a cryptocurrency or fiat currency.
    """
    symbol = models.CharField(max_length=10, unique=True)  # BTC, ETH, USDT, etc.
    name = models.CharField(max_length=100)  # Bitcoin, Ethereum, Tether USD
    is_crypto = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    precision = models.PositiveIntegerField(default=8)  # Decimal places
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'currencies'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ['symbol']
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"


class TradingPair(models.Model):
    """
    Represents a trading pair (e.g., BTC/USDT, ETH/USDT).
    """
    MARKET_TYPES = [
        ('spot', 'Spot'),
        ('futures', 'Futures'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    base_currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE, 
        related_name='base_pairs'
    )
    quote_currency = models.ForeignKey(
        Currency, 
        on_delete=models.CASCADE, 
        related_name='quote_pairs'
    )
    symbol = models.CharField(max_length=20, unique=True)  # BTCUSDT
    market_type = models.CharField(max_length=10, choices=MARKET_TYPES, default='spot')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Trading limits
    min_order_size = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    max_order_size = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    
    # Price precision
    price_precision = models.PositiveIntegerField(default=2)
    quantity_precision = models.PositiveIntegerField(default=6)
    
    # Fees (in percentage)
    maker_fee = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.001'))  # 0.1%
    taker_fee = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.001'))  # 0.1%
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trading_pairs'
        verbose_name = 'Trading Pair'
        verbose_name_plural = 'Trading Pairs'
        unique_together = ['base_currency', 'quote_currency', 'market_type']
        ordering = ['symbol']
    
    def __str__(self):
        return f"{self.symbol} ({self.market_type})"
    
    @property
    def display_name(self):
        """Return the display name for the trading pair."""
        return f"{self.base_currency.symbol}/{self.quote_currency.symbol}"


class MarketData(models.Model):
    """
    Stores real-time market data for trading pairs.
    """
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='market_data')
    
    # Price data
    price = models.DecimalField(max_digits=20, decimal_places=8)
    volume_24h = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Price changes
    change_24h = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    change_percent_24h = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    
    # High/Low
    high_24h = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    low_24h = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Order book data
    bid_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    ask_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    bid_quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    ask_quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'market_data'
        verbose_name = 'Market Data'
        verbose_name_plural = 'Market Data'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.trading_pair.symbol} - {self.price} @ {self.timestamp}"


class PriceHistory(models.Model):
    """
    Historical price data for charts and analysis.
    """
    INTERVAL_CHOICES = [
        ('1m', '1 Minute'),
        ('5m', '5 Minutes'),
        ('15m', '15 Minutes'),
        ('1h', '1 Hour'),
        ('4h', '4 Hours'),
        ('1d', '1 Day'),
    ]
    
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='price_history')
    interval = models.CharField(max_length=5, choices=INTERVAL_CHOICES)
    
    # OHLCV data
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    high_price = models.DecimalField(max_digits=20, decimal_places=8)
    low_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=20, decimal_places=8)
    
    timestamp = models.DateTimeField()
    
    class Meta:
        db_table = 'price_history'
        verbose_name = 'Price History'
        verbose_name_plural = 'Price History'
        unique_together = ['trading_pair', 'interval', 'timestamp']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.trading_pair.symbol} {self.interval} - {self.close_price} @ {self.timestamp}"