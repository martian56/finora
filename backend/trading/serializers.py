from rest_framework import serializers
from .models import Order, Trade, OrderBook, FuturesPosition
from markets.serializers import TradingPairSerializer


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    trading_pair = TradingPairSerializer(read_only=True)
    trading_pair_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'trading_pair', 'trading_pair_id', 'order_type',
            'side', 'quantity', 'price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class TradeSerializer(serializers.ModelSerializer):
    """Serializer for Trade model."""
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Trade
        fields = [
            'id', 'order', 'buyer', 'seller', 'quantity', 'price', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class OrderBookSerializer(serializers.ModelSerializer):
    """Serializer for OrderBook model."""
    trading_pair = TradingPairSerializer(read_only=True)
    
    class Meta:
        model = OrderBook
        fields = [
            'id', 'trading_pair', 'side', 'price', 'quantity', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class FuturesPositionSerializer(serializers.ModelSerializer):
    """Serializer for FuturesPosition model."""
    trading_pair = TradingPairSerializer(read_only=True)
    trading_pair_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FuturesPosition
        fields = [
            'id', 'user', 'trading_pair', 'trading_pair_id', 'side',
            'quantity', 'entry_price', 'current_price', 'leverage',
            'margin', 'pnl', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'current_price', 'pnl', 'created_at', 'updated_at']
