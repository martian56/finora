from django.db import models
from django.contrib.auth import get_user_model
from markets.models import TradingPair, Currency
from decimal import Decimal

User = get_user_model()


class TradingStats(models.Model):
    """
    Trading statistics for users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trading_stats')
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='trading_stats')
    
    # Trading metrics
    total_trades = models.PositiveIntegerField(default=0)
    winning_trades = models.PositiveIntegerField(default=0)
    losing_trades = models.PositiveIntegerField(default=0)
    
    # Volume metrics
    total_volume = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    total_fees_paid = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # P&L metrics
    total_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    realized_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    unrealized_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Performance metrics
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))  # Percentage
    average_win = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    average_loss = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Risk metrics
    max_drawdown = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trading_stats'
        verbose_name = 'Trading Statistics'
        verbose_name_plural = 'Trading Statistics'
        unique_together = ['user', 'trading_pair', 'period_start', 'period_end']
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.user.email} - {self.trading_pair.symbol} ({self.period_start} to {self.period_end})"
    
    def calculate_win_rate(self):
        """Calculate win rate percentage."""
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100
        return self.win_rate


class Portfolio(models.Model):
    """
    User portfolio summary.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='portfolios')
    
    # Portfolio metrics
    total_balance = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    available_balance = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    frozen_balance = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Performance metrics
    total_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    daily_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    weekly_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    monthly_pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Percentage changes
    daily_change_percent = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    weekly_change_percent = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    monthly_change_percent = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'portfolios'
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'
        unique_together = ['user', 'currency']
        ordering = ['currency__symbol']
    
    def __str__(self):
        return f"{self.user.email} - {self.currency.symbol}: {self.total_balance}"


class TradingSession(models.Model):
    """
    Trading session analytics.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trading_sessions')
    
    # Session details
    session_start = models.DateTimeField()
    session_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Session metrics
    trades_count = models.PositiveIntegerField(default=0)
    volume_traded = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    fees_paid = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    pnl = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Trading pairs used
    trading_pairs = models.JSONField(default=list)  # List of trading pair symbols
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trading_sessions'
        verbose_name = 'Trading Session'
        verbose_name_plural = 'Trading Sessions'
        ordering = ['-session_start']
    
    def __str__(self):
        return f"{self.user.email} - Session {self.session_start} ({self.trades_count} trades)"
    
    @property
    def duration(self):
        """Calculate session duration."""
        if self.session_end:
            return self.session_end - self.session_start
        return timezone.now() - self.session_start


class MarketAnalytics(models.Model):
    """
    Market-wide analytics and metrics.
    """
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='market_analytics')
    
    # Volume metrics
    volume_24h = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    volume_7d = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    volume_30d = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Price metrics
    price_change_24h = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    price_change_7d = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    price_change_30d = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    
    # Trading activity
    trades_count_24h = models.PositiveIntegerField(default=0)
    active_traders_24h = models.PositiveIntegerField(default=0)
    
    # Market depth
    bid_depth = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    ask_depth = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'market_analytics'
        verbose_name = 'Market Analytics'
        verbose_name_plural = 'Market Analytics'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.trading_pair.symbol} - Volume: {self.volume_24h}"