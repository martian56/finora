from rest_framework import serializers
from .models import TradingStats, Portfolio, TradingSession, MarketAnalytics


class TradingStatsSerializer(serializers.ModelSerializer):
    """Serializer for TradingStats model."""
    
    class Meta:
        model = TradingStats
        fields = [
            'id', 'user', 'total_trades', 'winning_trades', 'losing_trades',
            'total_volume', 'total_pnl', 'win_rate', 'avg_trade_size',
            'max_drawdown', 'sharpe_ratio', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio model."""
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'total_value', 'total_pnl', 'total_pnl_percentage',
            'daily_pnl', 'daily_pnl_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class TradingSessionSerializer(serializers.ModelSerializer):
    """Serializer for TradingSession model."""
    
    class Meta:
        model = TradingSession
        fields = [
            'id', 'user', 'start_time', 'end_time', 'trades_count',
            'volume_traded', 'pnl', 'session_duration', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class MarketAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for MarketAnalytics model."""
    
    class Meta:
        model = MarketAnalytics
        fields = [
            'id', 'trading_pair', 'volume_24h', 'price_change_24h',
            'high_24h', 'low_24h', 'market_cap', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
