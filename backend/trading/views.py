from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Order, Trade, OrderBook, FuturesPosition
from .serializers import OrderSerializer, TradeSerializer, OrderBookSerializer, FuturesPositionSerializer
from .services import OrderService


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('trading_pair')

    def perform_create(self, serializer):
        """Create order with balance management and execute matching."""
        try:
            # Extract validated data
            # The serializer uses trading_pair_id (write_only), not trading_pair
            from markets.models import TradingPair
            from .matching_engine import MatchingEngine
            
            trading_pair_id = serializer.validated_data['trading_pair_id']
            trading_pair = TradingPair.objects.get(id=trading_pair_id)
            
            order_type = serializer.validated_data['order_type']
            side = serializer.validated_data['side']
            quantity = serializer.validated_data['quantity']
            price = serializer.validated_data.get('price')
            
            # Use service to place order
            order = OrderService.place_order(
                user=self.request.user,
                trading_pair=trading_pair,
                order_type=order_type,
                side=side,
                quantity=quantity,
                price=price
            )
            
            # Try to execute the order immediately
            try:
                order = MatchingEngine.execute_order(order)
            except Exception as match_error:
                # Log the error but don't fail the order creation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error matching order {order.id}: {match_error}')
            
            # Update serializer instance
            serializer.instance = order
            
        except TradingPair.DoesNotExist:
            raise ValidationError('Trading pair not found')
        except DjangoValidationError as e:
            raise ValidationError(str(e))

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        try:
            OrderService.cancel_order(order)
            return Response({'message': 'Order cancelled successfully'})
        except DjangoValidationError as e:
            return Response({'error': str(e)}, 
                           status=status.HTTP_400_BAD_REQUEST)


class TradeViewSet(viewsets.ModelViewSet):
    """ViewSet for Trade model."""
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Trade.objects.filter(
            Q(buyer=self.request.user) | Q(seller=self.request.user)
        ).select_related('order', 'buyer', 'seller')


class OrderBookViewSet(viewsets.ModelViewSet):
    """ViewSet for OrderBook model."""
    queryset = OrderBook.objects.all()
    serializer_class = OrderBookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderBook.objects.select_related('trading_pair')


class FuturesPositionViewSet(viewsets.ModelViewSet):
    """ViewSet for FuturesPosition model."""
    queryset = FuturesPosition.objects.all()
    serializer_class = FuturesPositionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FuturesPosition.objects.filter(user=self.request.user).select_related('trading_pair')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a futures position."""
        position = self.get_object()
        if position.is_active:
            position.is_active = False
            position.save()
            return Response({'message': 'Position closed successfully'})
        return Response({'error': 'Position is already closed'}, 
                       status=status.HTTP_400_BAD_REQUEST)


class PlaceOrderView(APIView):
    """Place a new order."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            return Response(OrderSerializer(order).data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelOrderView(APIView):
    """Cancel an order."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.status = 'cancelled'
            order.save()
            return Response({'message': 'Order cancelled successfully'})
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class OrderStatusView(APIView):
    """Get order status."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class OpenOrdersView(APIView):
    """Get open orders."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(
            user=request.user,
            status__in=['pending', 'partial_filled']
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderHistoryView(APIView):
    """Get order history."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class TradeHistoryView(APIView):
    """Get trade history."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        trades = Trade.objects.filter(
            Q(buyer=request.user) | Q(seller=request.user)
        )
        serializer = TradeSerializer(trades, many=True)
        return Response(serializer.data)


class PlaceFuturesPositionView(APIView):
    """Place a futures position."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FuturesPositionSerializer(data=request.data)
        if serializer.is_valid():
            position = serializer.save(user=request.user)
            return Response(FuturesPositionSerializer(position).data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseFuturesPositionView(APIView):
    """Close a futures position."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, position_id):
        try:
            position = FuturesPosition.objects.get(id=position_id, user=request.user)
            position.status = 'closed'
            position.save()
            return Response({'message': 'Position closed successfully'})
        except FuturesPosition.DoesNotExist:
            return Response({'error': 'Position not found'}, 
                          status=status.HTTP_404_NOT_FOUND)