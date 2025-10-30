from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from .models import Order, Trade, OrderBook, FuturesPosition


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model."""
    
    list_display = [
        'id', 'user', 'trading_pair', 'order_type', 'side',
        'quantity', 'price', 'status', 'created_at', 'filled_at'
    ]
    list_filter = [
        'order_type', 'side', 'status', 'trading_pair',
        'created_at', 'filled_at'
    ]
    search_fields = [
        'user__email', 'user__username', 'trading_pair__base_currency__symbol',
        'trading_pair__quote_currency__symbol'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'filled_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'trading_pair', 'order_type', 'side')
        }),
        ('Order Details', {
            'fields': ('quantity', 'price', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'filled_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'user', 'trading_pair__base_currency', 'trading_pair__quote_currency'
        )
    
    def order_value(self, obj):
        """Calculate order value."""
        if obj.price:
            return f"${obj.quantity * obj.price:.2f}"
        return "Market Order"
    order_value.short_description = 'Order Value'
    
    actions = ['cancel_orders', 'mark_as_filled']
    
    def cancel_orders(self, request, queryset):
        """Cancel selected orders."""
        updated = queryset.filter(status__in=['pending', 'partial_filled']).update(status='cancelled')
        self.message_user(request, f'{updated} orders have been cancelled.')
    cancel_orders.short_description = 'Cancel selected orders'
    
    def mark_as_filled(self, request, queryset):
        """Mark orders as filled."""
        updated = queryset.filter(status__in=['pending', 'partial_filled']).update(
            status='filled', filled_at=timezone.now()
        )
        self.message_user(request, f'{updated} orders have been marked as filled.')
    mark_as_filled.short_description = 'Mark orders as filled'


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    """Admin for Trade model."""
    
    list_display = [
        'id', 'order', 'buyer', 'seller', 'quantity',
        'price', 'trade_value', 'created_at'
    ]
    list_filter = ['created_at', 'order__trading_pair']
    search_fields = [
        'buyer__email', 'seller__email', 'order__trading_pair__base_currency__symbol'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Trade Information', {
            'fields': ('order', 'buyer', 'seller')
        }),
        ('Trade Details', {
            'fields': ('quantity', 'price', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'order__trading_pair__base_currency', 'order__trading_pair__quote_currency',
            'buyer', 'seller'
        )
    
    def trade_value(self, obj):
        """Calculate trade value."""
        return f"${obj.quantity * obj.price:.2f}"
    trade_value.short_description = 'Trade Value'


@admin.register(OrderBook)
class OrderBookAdmin(admin.ModelAdmin):
    """Admin for OrderBook model."""
    
    list_display = [
        'trading_pair', 'side', 'price', 'quantity',
        'total_value', 'order_count', 'updated_at'
    ]
    list_filter = ['side', 'trading_pair', 'updated_at']
    search_fields = ['trading_pair__base_currency__symbol', 'trading_pair__quote_currency__symbol']
    ordering = ['-updated_at']
    readonly_fields = ['updated_at']
    date_hierarchy = 'updated_at'
    
    fieldsets = (
        ('Order Book Entry', {
            'fields': ('trading_pair', 'side', 'price', 'quantity', 'order_count', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'trading_pair__base_currency', 'trading_pair__quote_currency'
        )
    
    def total_value(self, obj):
        """Calculate total value."""
        return f"${obj.price * obj.quantity:.2f}"
    total_value.short_description = 'Total Value'


@admin.register(FuturesPosition)
class FuturesPositionAdmin(admin.ModelAdmin):
    """Admin for FuturesPosition model."""
    
    list_display = [
        'id', 'user', 'trading_pair', 'side', 'size',
        'entry_price', 'mark_price', 'leverage', 'initial_margin',
        'unrealized_pnl', 'status', 'created_at'
    ]
    list_filter = [
        'side', 'status', 'trading_pair', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__username', 'trading_pair__base_currency__symbol'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'closed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Position Information', {
            'fields': ('user', 'trading_pair', 'side', 'status')
        }),
        ('Position Details', {
            'fields': ('size', 'entry_price', 'mark_price', 'leverage', 'initial_margin', 'maintenance_margin')
        }),
        ('P&L Information', {
            'fields': ('unrealized_pnl', 'realized_pnl'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'user', 'trading_pair__base_currency', 'trading_pair__quote_currency'
        )
    
    def pnl_percentage(self, obj):
        """Calculate PnL percentage."""
        if obj.initial_margin > 0:
            percentage = (obj.unrealized_pnl / obj.initial_margin) * 100
            if percentage >= 0:
                return format_html('<span style="color: green;">+{:.2f}%</span>', percentage)
            else:
                return format_html('<span style="color: red;">{:.2f}%</span>', percentage)
        return "N/A"
    pnl_percentage.short_description = 'PnL %'
    
    actions = ['close_positions']
    
    def close_positions(self, request, queryset):
        """Close selected positions."""
        updated = queryset.filter(status='open').update(
            status='closed', closed_at=timezone.now()
        )
        self.message_user(request, f'{updated} positions have been closed.')
    close_positions.short_description = 'Close selected positions'