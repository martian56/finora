from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from markets.models import TradingPair, MarketData
from trading.models import Order, Trade
from wallets.models import Wallet, Transaction
from api_keys.models import APIKey
from notifications.models import Notification


class FinoraAdminSite(AdminSite):
    """Custom admin site for Finora."""
    
    site_header = "Finora Admin"
    site_title = "Finora Admin Portal"
    index_title = "Welcome to Finora Administration"
    
    def index(self, request, extra_context=None):
        """Custom admin dashboard with key metrics."""
        
        # Get key metrics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        
        total_trading_pairs = TradingPair.objects.filter(status='active').count()
        
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        filled_orders = Order.objects.filter(status='filled').count()
        
        total_trades = Trade.objects.count()
        today_trades = Trade.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
        
        total_wallets = Wallet.objects.count()
        total_balance = Wallet.objects.aggregate(
            total=Sum('balance')
        )['total'] or 0
        
        active_api_keys = APIKey.objects.filter(status='active').count()
        
        unread_notifications = Notification.objects.filter(is_read=False).count()
        
        # Recent activity
        recent_orders = Order.objects.select_related(
            'user', 'trading_pair__base_currency', 'trading_pair__quote_currency'
        ).order_by('-created_at')[:10]
        
        recent_trades = Trade.objects.select_related(
            'buyer', 'seller', 'order__trading_pair__base_currency'
        ).order_by('-created_at')[:10]
        
        # Chart data for the last 7 days
        chart_data = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            daily_trades = Trade.objects.filter(created_at__date=date).count()
            daily_volume = Trade.objects.filter(created_at__date=date).aggregate(
                volume=Sum('quantity')
            )['volume'] or 0
            
            chart_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'trades': daily_trades,
                'volume': float(daily_volume)
            })
        
        chart_data.reverse()  # Show oldest to newest
        
        extra_context = extra_context or {}
        extra_context.update({
            'metrics': {
                'total_users': total_users,
                'active_users': active_users,
                'verified_users': verified_users,
                'total_trading_pairs': total_trading_pairs,
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'filled_orders': filled_orders,
                'total_trades': total_trades,
                'today_trades': today_trades,
                'total_wallets': total_wallets,
                'total_balance': total_balance,
                'active_api_keys': active_api_keys,
                'unread_notifications': unread_notifications,
            },
            'recent_orders': recent_orders,
            'recent_trades': recent_trades,
            'chart_data': chart_data,
        })
        
        return super().index(request, extra_context)
    
    def get_urls(self):
        """Add custom admin URLs."""
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
            path('user-management/', self.admin_view(self.user_management_view), name='user_management'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        """Custom analytics view."""
        context = {
            'title': 'Analytics Dashboard',
            'has_permission': request.user.is_staff,
        }
        return render(request, 'admin/analytics.html', context)
    
    def user_management_view(self, request):
        """Custom user management view."""
        context = {
            'title': 'User Management',
            'has_permission': request.user.is_staff,
        }
        return render(request, 'admin/user_management.html', context)


# Create custom admin site instance
admin_site = FinoraAdminSite(name='finora_admin')

# Register all models with the custom admin site
from accounts.admin import UserAdmin
from markets.admin import CurrencyAdmin, TradingPairAdmin, MarketDataAdmin, PriceHistoryAdmin
from trading.admin import OrderAdmin, TradeAdmin, OrderBookAdmin, FuturesPositionAdmin
from wallets.admin import WalletAdmin, TransactionAdmin, DepositAdmin, WithdrawalAdmin
from api_keys.admin import APIKeyAdmin, APIKeyUsageAdmin
from notifications.admin import NotificationAdmin, PriceAlertAdmin
from analytics.admin import TradingStatsAdmin, PortfolioAdmin, TradingSessionAdmin, MarketAnalyticsAdmin

# Import models
from accounts.models import User
from markets.models import Currency, TradingPair, MarketData, PriceHistory
from trading.models import Order, Trade, OrderBook, FuturesPosition
from wallets.models import Wallet, Transaction, Deposit, Withdrawal
from api_keys.models import APIKey, APIKeyUsage
from notifications.models import Notification, PriceAlert
from analytics.models import TradingStats, Portfolio, TradingSession, MarketAnalytics

# Register models with custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(Currency, CurrencyAdmin)
admin_site.register(TradingPair, TradingPairAdmin)
admin_site.register(MarketData, MarketDataAdmin)
admin_site.register(PriceHistory, PriceHistoryAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(Trade, TradeAdmin)
admin_site.register(OrderBook, OrderBookAdmin)
admin_site.register(FuturesPosition, FuturesPositionAdmin)
admin_site.register(Wallet, WalletAdmin)
admin_site.register(Transaction, TransactionAdmin)
admin_site.register(Deposit, DepositAdmin)
admin_site.register(Withdrawal, WithdrawalAdmin)
admin_site.register(APIKey, APIKeyAdmin)
admin_site.register(APIKeyUsage, APIKeyUsageAdmin)
admin_site.register(Notification, NotificationAdmin)
admin_site.register(PriceAlert, PriceAlertAdmin)
admin_site.register(TradingStats, TradingStatsAdmin)
admin_site.register(Portfolio, PortfolioAdmin)
admin_site.register(TradingSession, TradingSessionAdmin)
admin_site.register(MarketAnalytics, MarketAnalyticsAdmin)
