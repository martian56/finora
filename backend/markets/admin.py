from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import Currency, TradingPair, MarketData, PriceHistory


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Admin for Currency model."""
    
    list_display = ['symbol', 'name', 'is_active', 'is_crypto', 'precision', 'created_at']
    list_filter = ['is_active', 'is_crypto', 'created_at']
    search_fields = ['symbol', 'name']
    ordering = ['symbol']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('symbol', 'name', 'is_crypto', 'is_active', 'precision')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def trading_pairs_count(self, obj):
        """Display count of trading pairs for this currency."""
        count = obj.base_pairs.count() + obj.quote_pairs.count()
        return count
    trading_pairs_count.short_description = 'Trading Pairs'


@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    """Admin for TradingPair model."""
    
    list_display = [
        'symbol', 'base_currency', 'quote_currency', 'market_type',
        'status', 'min_order_size', 'max_order_size', 'price_precision',
        'quantity_precision', 'created_at'
    ]
    list_filter = ['market_type', 'status', 'base_currency', 'quote_currency', 'created_at']
    search_fields = ['base_currency__symbol', 'quote_currency__symbol', 'symbol']
    ordering = ['symbol']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Trading Pair Information', {
            'fields': ('base_currency', 'quote_currency', 'symbol', 'market_type', 'status')
        }),
        ('Trading Parameters', {
            'fields': ('min_order_size', 'max_order_size', 'price_precision', 'quantity_precision')
        }),
        ('Fees', {
            'fields': ('maker_fee', 'taker_fee'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_name(self, obj):
        """Display trading pair display name."""
        return f"{obj.base_currency.symbol}/{obj.quote_currency.symbol}"
    display_name.short_description = 'Display Name'


@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    """Admin for MarketData model."""
    
    list_display = [
        'trading_pair', 'price', 'volume_24h', 'change_24h',
        'change_percent_24h', 'high_24h', 'low_24h', 'timestamp'
    ]
    list_filter = ['trading_pair', 'timestamp']
    search_fields = ['trading_pair__base_currency__symbol', 'trading_pair__quote_currency__symbol']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Market Data', {
            'fields': ('trading_pair', 'price', 'volume_24h')
        }),
        ('Price Changes', {
            'fields': ('change_24h', 'change_percent_24h', 'high_24h', 'low_24h')
        }),
        ('Order Book Data', {
            'fields': ('bid_price', 'ask_price', 'bid_quantity', 'ask_quantity'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def change_24h_display(self, obj):
        """Display 24h change with color coding."""
        if obj.change_24h >= 0:
            return format_html('<span style="color: green;">+{:.2f}%</span>', obj.change_24h)
        else:
            return format_html('<span style="color: red;">{:.2f}%</span>', obj.change_24h)
    change_24h_display.short_description = '24h Change'


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    """Admin for PriceHistory model."""
    
    list_display = [
        'trading_pair', 'interval', 'open_price', 'high_price', 
        'low_price', 'close_price', 'volume', 'timestamp'
    ]
    list_filter = ['trading_pair', 'interval', 'timestamp']
    search_fields = ['trading_pair__base_currency__symbol', 'trading_pair__quote_currency__symbol']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Price History', {
            'fields': ('trading_pair', 'interval', 'timestamp')
        }),
        ('OHLCV Data', {
            'fields': ('open_price', 'high_price', 'low_price', 'close_price', 'volume')
        }),
    )
    
    # Add date hierarchy for easy navigation
    date_hierarchy = 'timestamp'