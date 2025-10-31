"""
Simple Order Matching Engine for executing trades.
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Order, Trade, OrderBook
from .services import OrderService


class MatchingEngine:
    """
    Simple matching engine that matches market/limit orders with the order book.
    """
    
    @staticmethod
    @transaction.atomic
    def match_market_order(order):
        """
        Execute a market order immediately against the best available prices.
        
        For BUY orders: Match against asks (sell orders) starting from lowest price
        For SELL orders: Match against bids (buy orders) starting from highest price
        """
        if order.order_type != 'market':
            raise ValueError('This method only handles market orders')
        
        if order.status != 'pending':
            return order
        
        remaining_quantity = order.quantity - order.filled_quantity
        
        if order.side == 'buy':
            # Get best asks (lowest prices first)
            available_orders = Order.objects.filter(
                trading_pair=order.trading_pair,
                side='sell',
                status__in=['pending', 'partial_filled'],
                order_type='limit'  # Only match against limit orders in order book
            ).exclude(
                user=order.user  # Don't match own orders
            ).order_by('price', 'created_at')  # Best price first, then FIFO
            
        else:  # sell
            # Get best bids (highest prices first)
            available_orders = Order.objects.filter(
                trading_pair=order.trading_pair,
                side='buy',
                status__in=['pending', 'partial_filled'],
                order_type='limit'
            ).exclude(
                user=order.user
            ).order_by('-price', 'created_at')  # Best price first, then FIFO
        
        # Execute trades
        for counter_order in available_orders:
            if remaining_quantity <= 0:
                break
            
            # Calculate match quantity
            counter_remaining = counter_order.quantity - counter_order.filled_quantity
            match_quantity = min(remaining_quantity, counter_remaining)
            
            # Execution price is the counter order's price (price improvement for market order)
            execution_price = counter_order.price
            
            # Fill both orders
            OrderService.fill_order(order, match_quantity, execution_price)
            OrderService.fill_order(counter_order, match_quantity, execution_price)
            
            # Create trade record
            Trade.objects.create(
                order=order,
                buyer=order.user if order.side == 'buy' else counter_order.user,
                seller=counter_order.user if order.side == 'buy' else order.user,
                quantity=match_quantity,
                price=execution_price,
                timestamp=timezone.now()
            )
            
            remaining_quantity -= match_quantity
        
        # Reload order to get updated status
        order.refresh_from_db()
        
        # If order not fully filled, cancel the remaining (market orders should fill or kill)
        if order.status == 'pending' or order.status == 'partial_filled':
            # For market orders, we cancel unfilled portion
            order.status = 'partial_filled' if order.filled_quantity > 0 else 'cancelled'
            order.save()
        
        return order
    
    @staticmethod
    @transaction.atomic
    def match_limit_order(order):
        """
        Try to match a limit order immediately if possible.
        
        For BUY orders: Match against asks at or below the limit price
        For SELL orders: Match against bids at or above the limit price
        """
        if order.order_type != 'limit':
            raise ValueError('This method only handles limit orders')
        
        if order.status != 'pending':
            return order
        
        remaining_quantity = order.quantity - order.filled_quantity
        
        if order.side == 'buy':
            # Get asks at or below our buy price
            available_orders = Order.objects.filter(
                trading_pair=order.trading_pair,
                side='sell',
                status__in=['pending', 'partial_filled'],
                order_type='limit',
                price__lte=order.price  # Seller asking <= our max buy price
            ).exclude(
                user=order.user
            ).order_by('price', 'created_at')
            
        else:  # sell
            # Get bids at or above our sell price
            available_orders = Order.objects.filter(
                trading_pair=order.trading_pair,
                side='buy',
                status__in=['pending', 'partial_filled'],
                order_type='limit',
                price__gte=order.price  # Buyer bidding >= our min sell price
            ).exclude(
                user=order.user
            ).order_by('-price', 'created_at')
        
        # Execute trades
        for counter_order in available_orders:
            if remaining_quantity <= 0:
                break
            
            # Calculate match quantity
            counter_remaining = counter_order.quantity - counter_order.filled_quantity
            match_quantity = min(remaining_quantity, counter_remaining)
            
            # Execution price: Use the counter order's price (maker gets their price)
            execution_price = counter_order.price
            
            # Fill both orders
            OrderService.fill_order(order, match_quantity, execution_price)
            OrderService.fill_order(counter_order, match_quantity, execution_price)
            
            # Create trade record
            Trade.objects.create(
                order=order,
                buyer=order.user if order.side == 'buy' else counter_order.user,
                seller=counter_order.user if order.side == 'buy' else order.user,
                quantity=match_quantity,
                price=execution_price,
                timestamp=timezone.now()
            )
            
            remaining_quantity -= match_quantity
        
        # Reload order to get updated status
        order.refresh_from_db()
        
        return order
    
    @staticmethod
    def execute_order(order):
        """
        Execute an order based on its type.
        """
        if order.order_type == 'market':
            return MatchingEngine.match_market_order(order)
        elif order.order_type == 'limit':
            return MatchingEngine.match_limit_order(order)
        else:
            raise ValueError(f'Unknown order type: {order.order_type}')

