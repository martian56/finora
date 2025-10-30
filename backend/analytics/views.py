from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import TradingStats, Portfolio, TradingSession, MarketAnalytics
from .serializers import TradingStatsSerializer, PortfolioSerializer, TradingSessionSerializer, MarketAnalyticsSerializer


class TradingStatsViewSet(viewsets.ModelViewSet):
    """ViewSet for TradingStats model."""
    queryset = TradingStats.objects.all()
    serializer_class = TradingStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TradingStats.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PortfolioViewSet(viewsets.ModelViewSet):
    """ViewSet for Portfolio model."""
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TradingSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for TradingSession model."""
    queryset = TradingSession.objects.all()
    serializer_class = TradingSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TradingSession.objects.filter(user=self.request.user).order_by('-start_time')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MarketAnalyticsViewSet(viewsets.ModelViewSet):
    """ViewSet for MarketAnalytics model."""
    queryset = MarketAnalytics.objects.all()
    serializer_class = MarketAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MarketAnalytics.objects.select_related('trading_pair').order_by('-timestamp')


class DashboardView(APIView):
    """Get dashboard data."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # This would return comprehensive dashboard data
        return Response({
            'message': 'Dashboard data not implemented yet',
            'user': request.user.email
        })


class PerformanceView(APIView):
    """Get performance analytics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # This would return performance metrics
        return Response({
            'message': 'Performance analytics not implemented yet',
            'user': request.user.email
        })


class PortfolioSummaryView(APIView):
    """Get portfolio summary."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        portfolios = Portfolio.objects.filter(user=request.user)
        serializer = PortfolioSerializer(portfolios, many=True)
        return Response(serializer.data)


class TradingHistoryView(APIView):
    """Get trading history analytics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # This would return trading history analytics
        return Response({
            'message': 'Trading history analytics not implemented yet',
            'user': request.user.email
        })