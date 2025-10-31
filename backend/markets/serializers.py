from rest_framework import serializers
from .models import Currency, TradingPair, MarketData, PriceHistory


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for Currency model."""
    
    class Meta:
        model = Currency
        fields = ['id', 'symbol', 'name', 'is_active', 'created_at']


class TradingPairSerializer(serializers.ModelSerializer):
    """Serializer for TradingPair model."""
    base_currency = CurrencySerializer(read_only=True)
    quote_currency = CurrencySerializer(read_only=True)
    base_currency_id = serializers.IntegerField(write_only=True)
    quote_currency_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TradingPair
        fields = [
            'id', 'symbol', 'base_currency', 'quote_currency', 'base_currency_id', 
            'quote_currency_id', 'market_type', 'status', 'min_order_size', 
            'max_order_size', 'price_precision', 'quantity_precision', 
            'maker_fee', 'taker_fee', 'created_at'
        ]


class MarketDataSerializer(serializers.ModelSerializer):
    """Serializer for MarketData model."""
    trading_pair = TradingPairSerializer(read_only=True)
    trading_pair_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MarketData
        fields = [
            'id', 'trading_pair', 'trading_pair_id', 'price', 'volume_24h',
            'change_24h', 'change_percent_24h', 'high_24h', 'low_24h', 
            'bid_price', 'ask_price', 'bid_quantity', 'ask_quantity', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer for PriceHistory model."""
    trading_pair = TradingPairSerializer(read_only=True)
    trading_pair_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PriceHistory
        fields = [
            'id', 'trading_pair', 'trading_pair_id', 'price', 'volume',
            'timestamp'
        ]
