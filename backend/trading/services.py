from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from wallets.models import Wallet, Transaction
from .models import Order


class OrderService:
    """Service to handle order placement and balance management."""
    
    @staticmethod
    @transaction.atomic
    def place_order(user, trading_pair, order_type, side, quantity, price=None):
        """
        Place an order and handle balance freezing.
        
        For BUY orders: Freeze quote currency (e.g., USDT)
        For SELL orders: Freeze base currency (e.g., BTC)
        """
        quantity = Decimal(str(quantity))
        price = Decimal(str(price)) if price else None
        
        # Determine which currency to freeze
        if side == 'buy':
            currency = trading_pair.quote_currency
            # For market orders, we need an estimated price
            if order_type == 'market':
                # Use the last market price or a default
                from markets.models import MarketData
                market_data = MarketData.objects.filter(
                    trading_pair=trading_pair
                ).order_by('-last_updated').first()
                estimated_price = market_data.price if market_data else Decimal('50000')
            else:
                estimated_price = price
            
            required_amount = quantity * estimated_price
        else:  # sell
            currency = trading_pair.base_currency
            required_amount = quantity
        
        # Get or create wallet
        wallet, created = Wallet.objects.get_or_create(
            user=user,
            currency=currency,
            defaults={'balance': Decimal('0'), 'frozen_balance': Decimal('0')}
        )
        
        # Check if user has sufficient balance
        if wallet.available_balance < required_amount:
            raise ValidationError(
                f'Insufficient {currency.symbol} balance. '
                f'Required: {required_amount}, Available: {wallet.available_balance}'
            )
        
        # Create the order
        order = Order.objects.create(
            user=user,
            trading_pair=trading_pair,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            status='pending'
        )
        
        # Freeze the required amount
        wallet.frozen_balance += required_amount
        wallet.save(update_fields=['frozen_balance', 'updated_at'])
        
        # Create transaction record
        Transaction.objects.create(
            user=user,
            wallet=wallet,
            transaction_type='trade',
            status='pending',
            amount=-required_amount,
            balance_before=wallet.balance + wallet.frozen_balance - required_amount,
            balance_after=wallet.balance,
            reference_id=f'ORDER_{order.id}',
            description=f'{side.upper()} order placed for {quantity} {trading_pair.base_currency.symbol}'
        )
        
        return order
    
    @staticmethod
    @transaction.atomic
    def cancel_order(order):
        """Cancel an order and unfreeze the balance."""
        if order.status not in ['pending', 'partial_filled']:
            raise ValidationError('Only pending or partially filled orders can be cancelled')
        
        # Determine which currency was frozen
        if order.side == 'buy':
            currency = order.trading_pair.quote_currency
            # Calculate the amount that was frozen
            if order.order_type == 'market':
                from markets.models import MarketData
                market_data = MarketData.objects.filter(
                    trading_pair=order.trading_pair
                ).order_by('-last_updated').first()
                estimated_price = market_data.price if market_data else Decimal('50000')
            else:
                estimated_price = order.price
            
            frozen_amount = (order.quantity - order.filled_quantity) * estimated_price
        else:  # sell
            currency = order.trading_pair.base_currency
            frozen_amount = order.quantity - order.filled_quantity
        
        # Get wallet
        wallet = Wallet.objects.get(user=order.user, currency=currency)
        
        # Unfreeze the amount
        wallet.frozen_balance -= frozen_amount
        if wallet.frozen_balance < 0:
            wallet.frozen_balance = Decimal('0')
        wallet.save(update_fields=['frozen_balance', 'updated_at'])
        
        # Update order status
        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
        
        # Create transaction record
        Transaction.objects.create(
            user=order.user,
            wallet=wallet,
            transaction_type='trade',
            status='completed',
            amount=frozen_amount,
            balance_before=wallet.balance,
            balance_after=wallet.balance,
            reference_id=f'ORDER_CANCEL_{order.id}',
            description=f'Order cancelled: {order.side.upper()} {order.quantity} {order.trading_pair.base_currency.symbol}'
        )
        
        return order
    
    @staticmethod
    @transaction.atomic
    def fill_order(order, filled_quantity, execution_price):
        """
        Fill an order (partially or fully) and update balances.
        
        For BUY: Unfreeze quote currency, add base currency
        For SELL: Unfreeze base currency, add quote currency
        """
        filled_quantity = Decimal(str(filled_quantity))
        execution_price = Decimal(str(execution_price))
        
        if order.side == 'buy':
            # Unfreeze quote currency (what was frozen)
            quote_wallet = Wallet.objects.get(
                user=order.user,
                currency=order.trading_pair.quote_currency
            )
            frozen_amount = filled_quantity * execution_price
            quote_wallet.frozen_balance -= frozen_amount
            quote_wallet.balance -= frozen_amount
            quote_wallet.save()
            
            # Add base currency (what user receives)
            base_wallet, created = Wallet.objects.get_or_create(
                user=order.user,
                currency=order.trading_pair.base_currency,
                defaults={'balance': Decimal('0'), 'frozen_balance': Decimal('0')}
            )
            base_wallet.balance += filled_quantity
            base_wallet.save()
            
        else:  # sell
            # Unfreeze base currency (what was frozen)
            base_wallet = Wallet.objects.get(
                user=order.user,
                currency=order.trading_pair.base_currency
            )
            base_wallet.frozen_balance -= filled_quantity
            base_wallet.balance -= filled_quantity
            base_wallet.save()
            
            # Add quote currency (what user receives)
            quote_wallet, created = Wallet.objects.get_or_create(
                user=order.user,
                currency=order.trading_pair.quote_currency,
                defaults={'balance': Decimal('0'), 'frozen_balance': Decimal('0')}
            )
            received_amount = filled_quantity * execution_price
            quote_wallet.balance += received_amount
            quote_wallet.save()
        
        # Update order
        order.filled_quantity += filled_quantity
        if order.filled_quantity >= order.quantity:
            order.status = 'filled'
        else:
            order.status = 'partial_filled'
        order.save()
        
        return order

