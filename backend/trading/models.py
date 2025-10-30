from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from markets.models import TradingPair


class Order(models.Model):
    """
    Trading orders (both spot and futures).
    """
    ORDER_TYPES = [
        ('market', 'Market'),
        ('limit', 'Limit'),
        ('stop', 'Stop'),
        ('stop_limit', 'Stop Limit'),
    ]
    
    ORDER_SIDES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('partial_filled', 'Partially Filled'),
        ('filled', 'Filled'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    side = models.CharField(max_length=10, choices=ORDER_SIDES)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    
    # Price and quantity
    price = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    quantity = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    
    # Filled information
    filled_quantity = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        default=Decimal('0')
    )
    remaining_quantity = models.DecimalField(
        max_digits=20, 
        decimal_places=8
    )
    
    # Average fill price
    average_fill_price = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        null=True, 
        blank=True
    )
    
    # Fees
    maker_fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    taker_fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    total_fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Time in force
    time_in_force = models.CharField(
        max_length=10,
        choices=[
            ('GTC', 'Good Till Cancelled'),
            ('IOC', 'Immediate or Cancel'),
            ('FOK', 'Fill or Kill'),
        ],
        default='GTC'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    filled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.side} {self.quantity} {self.trading_pair.symbol} @ {self.price}"
    
    def save(self, *args, **kwargs):
        # Calculate remaining quantity
        self.remaining_quantity = self.quantity - self.filled_quantity
        super().save(*args, **kwargs)
    
    @property
    def is_filled(self):
        """Check if the order is completely filled."""
        return self.status == 'filled'
    
    @property
    def is_partial_filled(self):
        """Check if the order is partially filled."""
        return self.status == 'partial_filled'
    
    @property
    def fill_percentage(self):
        """Calculate the fill percentage."""
        if self.quantity > 0:
            return (self.filled_quantity / self.quantity) * 100
        return 0


class Trade(models.Model):
    """
    Individual trade executions.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='trades')
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='trades')
    
    # Trade participants
    buyer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='buy_trades'
    )
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sell_trades'
    )
    
    # Trade details
    price = models.DecimalField(max_digits=20, decimal_places=8)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    total_value = models.DecimalField(max_digits=20, decimal_places=8)
    
    # Fees
    buyer_fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    seller_fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Trade ID
    trade_id = models.CharField(max_length=50, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trades'
        verbose_name = 'Trade'
        verbose_name_plural = 'Trades'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.trade_id} - {self.quantity} {self.trading_pair.symbol} @ {self.price}"
    
    def save(self, *args, **kwargs):
        # Calculate total value
        self.total_value = self.price * self.quantity
        super().save(*args, **kwargs)


class OrderBook(models.Model):
    """
    Order book for each trading pair.
    """
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='order_book')
    
    # Order book levels
    price = models.DecimalField(max_digits=20, decimal_places=8)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    side = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    
    # Number of orders at this price level
    order_count = models.PositiveIntegerField(default=1)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_book'
        verbose_name = 'Order Book Entry'
        verbose_name_plural = 'Order Book Entries'
        unique_together = ['trading_pair', 'price', 'side']
        ordering = ['-price']  # Highest price first for buy orders
    
    def __str__(self):
        return f"{self.trading_pair.symbol} - {self.side} {self.quantity} @ {self.price}"


class FuturesPosition(models.Model):
    """
    Futures trading positions.
    """
    POSITION_SIDES = [
        ('long', 'Long'),
        ('short', 'Short'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('liquidated', 'Liquidated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='futures_positions')
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='futures_positions')
    
    # Position details
    side = models.CharField(max_length=10, choices=POSITION_SIDES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Size and price
    size = models.DecimalField(max_digits=20, decimal_places=8)  # Position size
    entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    mark_price = models.DecimalField(max_digits=20, decimal_places=8)  # Current mark price
    
    # P&L
    unrealized_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    realized_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Margin
    initial_margin = models.DecimalField(max_digits=20, decimal_places=8)
    maintenance_margin = models.DecimalField(max_digits=20, decimal_places=8)
    
    # Leverage
    leverage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'futures_positions'
        verbose_name = 'Futures Position'
        verbose_name_plural = 'Futures Positions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.side} {self.size} {self.trading_pair.symbol}"
    
    def calculate_unrealized_pnl(self):
        """Calculate unrealized P&L based on current mark price."""
        if self.side == 'long':
            self.unrealized_pnl = (self.mark_price - self.entry_price) * self.size
        else:  # short
            self.unrealized_pnl = (self.entry_price - self.mark_price) * self.size
        return self.unrealized_pnl