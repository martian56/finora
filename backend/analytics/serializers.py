from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import TradingStats, Portfolio, TradingSession, MarketAnalytics


class TradingStatsSerializer(serializers.ModelSerializer):
    """Serializer for TradingStats model."""
    
    class Meta:
        model = TradingStats
        fields = [
            'id', 'user', 'trading_pair', 'total_trades', 'winning_trades', 
            'losing_trades', 'total_volume', 'total_fees_paid', 'total_pnl',
            'realized_pnl', 'unrealized_pnl', 'win_rate', 'average_win',
            'average_loss', 'max_drawdown', 'sharpe_ratio', 'period_start',
            'period_end', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio model."""
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'currency', 'total_balance', 'available_balance',
            'frozen_balance', 'total_pnl', 'daily_pnl', 'weekly_pnl',
            'monthly_pnl', 'daily_change_percent', 'weekly_change_percent',
            'monthly_change_percent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class TradingSessionSerializer(serializers.ModelSerializer):
    """Serializer for TradingSession model."""
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = TradingSession
        fields = [
            'id', 'user', 'session_start', 'session_end', 'is_active',
            'trades_count', 'volume_traded', 'fees_paid', 'pnl',
            'trading_pairs', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.CharField())
    def get_duration(self, obj):
        """Get session duration as string."""
        if obj.session_end:
            duration = obj.session_end - obj.session_start
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "Active"


class MarketAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for MarketAnalytics model."""
    
    class Meta:
        model = MarketAnalytics
        fields = [
            'id', 'trading_pair', 'volume_24h', 'volume_7d', 'volume_30d',
            'price_change_24h', 'price_change_7d', 'price_change_30d',
            'trades_count_24h', 'active_traders_24h', 'bid_depth',
            'ask_depth', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
