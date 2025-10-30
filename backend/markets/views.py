from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Currency, TradingPair, MarketData, PriceHistory
from .serializers import CurrencySerializer, TradingPairSerializer, MarketDataSerializer, PriceHistorySerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    """ViewSet for Currency model."""
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Currency.objects.filter(is_active=True)


class TradingPairViewSet(viewsets.ModelViewSet):
    """ViewSet for TradingPair model."""
    queryset = TradingPair.objects.all()
    serializer_class = TradingPairSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return TradingPair.objects.filter(status='active').select_related('base_currency', 'quote_currency')


class MarketDataViewSet(viewsets.ModelViewSet):
    """ViewSet for MarketData model."""
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return MarketData.objects.select_related('trading_pair')


class PriceHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for PriceHistory model."""
    queryset = PriceHistory.objects.all()
    serializer_class = PriceHistorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = PriceHistory.objects.select_related('trading_pair')
        
        # Filter by trading pair if provided
        trading_pair_id = self.request.query_params.get('trading_pair')
        if trading_pair_id:
            queryset = queryset.filter(trading_pair_id=trading_pair_id)
        
        return queryset.order_by('-timestamp')


class TickerListView(APIView):
    """Get all trading pair tickers."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        trading_pairs = TradingPair.objects.filter(status='active')
        tickers = []
        
        for pair in trading_pairs:
            market_data = MarketData.objects.filter(
                trading_pair=pair
            ).order_by('-timestamp').first()
            
            if market_data:
                tickers.append({
                    'symbol': pair.symbol,
                    'price': float(market_data.price),
                    'change_24h': float(market_data.change_24h),
                    'change_percent_24h': float(market_data.change_percent_24h),
                    'volume_24h': float(market_data.volume_24h),
                    'high_24h': float(market_data.high_24h),
                    'low_24h': float(market_data.low_24h),
                })
        
        return Response(tickers)


class TickerDetailView(APIView):
    """Get specific trading pair ticker."""
    permission_classes = [AllowAny]
    
    def get(self, request, symbol):
        try:
            trading_pair = TradingPair.objects.get(symbol=symbol)
            market_data = MarketData.objects.filter(
                trading_pair=trading_pair
            ).order_by('-timestamp').first()
            
            if market_data:
                ticker = {
                    'symbol': trading_pair.symbol,
                    'price': float(market_data.price),
                    'change_24h': float(market_data.change_24h),
                    'change_percent_24h': float(market_data.change_percent_24h),
                    'volume_24h': float(market_data.volume_24h),
                    'high_24h': float(market_data.high_24h),
                    'low_24h': float(market_data.low_24h),
                }
                return Response(ticker)
            return Response({'error': 'No market data found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        except TradingPair.DoesNotExist:
            return Response({'error': 'Trading pair not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class OrderBookView(APIView):
    """Get order book for a trading pair."""
    permission_classes = [AllowAny]
    
    def get(self, request, symbol):
        try:
            trading_pair = TradingPair.objects.get(symbol=symbol)
            # This would be implemented with actual order book data
            return Response({
                'symbol': symbol,
                'bids': [],
                'asks': []
            })
        except TradingPair.DoesNotExist:
            return Response({'error': 'Trading pair not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class KlinesView(APIView):
    """Get kline/candlestick data for a trading pair."""
    permission_classes = [AllowAny]
    
    def get(self, request, symbol):
        try:
            trading_pair = TradingPair.objects.get(symbol=symbol)
            interval = request.GET.get('interval', '1h')
            limit = int(request.GET.get('limit', 100))
            
            klines = PriceHistory.objects.filter(
                trading_pair=trading_pair,
                interval=interval
            ).order_by('-timestamp')[:limit]
            
            kline_data = []
            for kline in klines:
                kline_data.append([
                    int(kline.timestamp.timestamp() * 1000),  # Open time
                    float(kline.open_price),  # Open
                    float(kline.high_price),   # High
                    float(kline.low_price),    # Low
                    float(kline.close_price),  # Close
                    float(kline.volume),       # Volume
                ])
            
            return Response(kline_data)
        except TradingPair.DoesNotExist:
            return Response({'error': 'Trading pair not found'}, 
                          status=status.HTTP_404_NOT_FOUND)