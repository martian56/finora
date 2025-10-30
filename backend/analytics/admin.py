from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Sum, Count
from .models import TradingStats, Portfolio, TradingSession, MarketAnalytics


@admin.register(TradingStats)
class TradingStatsAdmin(admin.ModelAdmin):
    """Admin for TradingStats model."""
    
    list_display = [
        'user', 'trading_pair', 'total_trades', 'winning_trades', 'losing_trades',
        'win_rate', 'total_volume', 'total_pnl', 'sharpe_ratio',
        'updated_at'
    ]
    list_filter = ['updated_at', 'trading_pair']
    search_fields = ['user__email', 'user__username', 'trading_pair__base_currency__symbol']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'trading_pair')
        }),
        ('Trade Statistics', {
            'fields': ('total_trades', 'winning_trades', 'losing_trades', 'win_rate')
        }),
        ('Volume & PnL', {
            'fields': ('total_volume', 'total_pnl', 'realized_pnl', 'unrealized_pnl')
        }),
        ('Performance Metrics', {
            'fields': ('average_win', 'average_loss', 'max_drawdown', 'sharpe_ratio')
        }),
        ('Time Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('user', 'trading_pair__base_currency', 'trading_pair__quote_currency')
    
    def win_rate_display(self, obj):
        """Display win rate with color coding."""
        if obj.win_rate >= 60:
            return format_html('<span style="color: green;">{:.1f}%</span>', obj.win_rate)
        elif obj.win_rate >= 40:
            return format_html('<span style="color: orange;">{:.1f}%</span>', obj.win_rate)
        else:
            return format_html('<span style="color: red;">{:.1f}%</span>', obj.win_rate)
    win_rate_display.short_description = 'Win Rate'
    
    def pnl_display(self, obj):
        """Display PnL with color coding."""
        if obj.total_pnl >= 0:
            return format_html('<span style="color: green;">+${:.2f}</span>', obj.total_pnl)
        else:
            return format_html('<span style="color: red;">-${:.2f}</span>', abs(obj.total_pnl))
    pnl_display.short_description = 'Total PnL'


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Admin for Portfolio model."""
    
    list_display = [
        'user', 'currency', 'total_balance', 'total_pnl',
        'daily_pnl', 'daily_change_percent', 'updated_at'
    ]
    list_filter = ['currency', 'updated_at']
    search_fields = ['user__email', 'user__username', 'currency__symbol']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'currency')
        }),
        ('Balance Information', {
            'fields': ('total_balance', 'available_balance', 'frozen_balance')
        }),
        ('Performance Metrics', {
            'fields': ('total_pnl', 'daily_pnl', 'weekly_pnl', 'monthly_pnl')
        }),
        ('Percentage Changes', {
            'fields': ('daily_change_percent', 'weekly_change_percent', 'monthly_change_percent')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('user')
    
    def total_pnl_percentage_display(self, obj):
        """Display total PnL percentage with color coding."""
        if obj.total_pnl_percentage >= 0:
            return format_html('<span style="color: green;">+{:.2f}%</span>', obj.total_pnl_percentage)
        else:
            return format_html('<span style="color: red;">{:.2f}%</span>', obj.total_pnl_percentage)
    total_pnl_percentage_display.short_description = 'Total PnL %'
    
    def daily_pnl_percentage_display(self, obj):
        """Display daily PnL percentage with color coding."""
        if obj.daily_pnl_percentage >= 0:
            return format_html('<span style="color: green;">+{:.2f}%</span>', obj.daily_pnl_percentage)
        else:
            return format_html('<span style="color: red;">{:.2f}%</span>', obj.daily_pnl_percentage)
    daily_pnl_percentage_display.short_description = 'Daily PnL %'


@admin.register(TradingSession)
class TradingSessionAdmin(admin.ModelAdmin):
    """Admin for TradingSession model."""
    
    list_display = [
        'user', 'session_start', 'session_end', 'duration',
        'trades_count', 'volume_traded', 'pnl', 'created_at'
    ]
    list_filter = ['session_start', 'created_at']
    search_fields = ['user__email', 'user__username']
    ordering = ['-session_start']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'session_start'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'session_start', 'session_end', 'is_active')
        }),
        ('Session Statistics', {
            'fields': ('trades_count', 'volume_traded', 'fees_paid', 'pnl')
        }),
        ('Trading Pairs', {
            'fields': ('trading_pairs',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('user')
    
    def session_duration_display(self, obj):
        """Display session duration in a readable format."""
        if obj.session_duration:
            hours = obj.session_duration // 3600
            minutes = (obj.session_duration % 3600) // 60
            return f"{hours}h {minutes}m"
        return "N/A"
    session_duration_display.short_description = 'Duration'
    
    def pnl_display(self, obj):
        """Display PnL with color coding."""
        if obj.pnl >= 0:
            return format_html('<span style="color: green;">+${:.2f}</span>', obj.pnl)
        else:
            return format_html('<span style="color: red;">-${:.2f}</span>', abs(obj.pnl))
    pnl_display.short_description = 'PnL'


@admin.register(MarketAnalytics)
class MarketAnalyticsAdmin(admin.ModelAdmin):
    """Admin for MarketAnalytics model."""
    
    list_display = [
        'trading_pair', 'volume_24h', 'price_change_24h',
        'trades_count_24h', 'active_traders_24h', 'updated_at'
    ]
    list_filter = ['trading_pair', 'updated_at']
    search_fields = [
        'trading_pair__base_currency__symbol', 'trading_pair__quote_currency__symbol'
    ]
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'updated_at'
    
    fieldsets = (
        ('Trading Pair', {
            'fields': ('trading_pair',)
        }),
        ('Volume Metrics', {
            'fields': ('volume_24h', 'volume_7d', 'volume_30d')
        }),
        ('Price Changes', {
            'fields': ('price_change_24h', 'price_change_7d', 'price_change_30d')
        }),
        ('Trading Activity', {
            'fields': ('trades_count_24h', 'active_traders_24h')
        }),
        ('Market Depth', {
            'fields': ('bid_depth', 'ask_depth'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'trading_pair__base_currency', 'trading_pair__quote_currency'
        )
    
    def price_change_24h_display(self, obj):
        """Display 24h price change with color coding."""
        if obj.price_change_24h >= 0:
            return format_html('<span style="color: green;">+{:.2f}%</span>', obj.price_change_24h)
        else:
            return format_html('<span style="color: red;">{:.2f}%</span>', obj.price_change_24h)
    price_change_24h_display.short_description = '24h Change'
    
    def market_cap_display(self, obj):
        """Display market cap in a readable format."""
        if obj.market_cap:
            if obj.market_cap >= 1e9:
                return f"${obj.market_cap/1e9:.2f}B"
            elif obj.market_cap >= 1e6:
                return f"${obj.market_cap/1e6:.2f}M"
            elif obj.market_cap >= 1e3:
                return f"${obj.market_cap/1e3:.2f}K"
            else:
                return f"${obj.market_cap:.2f}"
        return "N/A"
    market_cap_display.short_description = 'Market Cap'
    
    actions = ['analyze_volume_trends', 'analyze_price_trends']
    
    def analyze_volume_trends(self, request, queryset):
        """Analyze volume trends."""
        avg_volume = queryset.aggregate(avg_volume=Avg('volume_24h'))['avg_volume']
        self.message_user(request, f'Average 24h volume: ${avg_volume:,.2f}')
    analyze_volume_trends.short_description = 'Analyze volume trends'
    
    def analyze_price_trends(self, request, queryset):
        """Analyze price trends."""
        positive_changes = queryset.filter(price_change_24h__gt=0).count()
        total_changes = queryset.count()
        if total_changes > 0:
            positive_percentage = (positive_changes / total_changes) * 100
            self.message_user(request, f'{positive_percentage:.1f}% of pairs had positive price changes.')
    analyze_price_trends.short_description = 'Analyze price trends'