from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from markets.models import Currency


class Wallet(models.Model):
    """
    User wallet for storing balances of different currencies.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    
    # Balance information
    balance = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    frozen_balance = models.DecimalField(
        max_digits=20, 
        decimal_places=8, 
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wallets'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        unique_together = ['user', 'currency']
        ordering = ['currency__symbol']
    
    def __str__(self):
        return f"{self.user.email} - {self.currency.symbol}: {self.balance}"
    
    @property
    def available_balance(self):
        """Return the available balance (total - frozen)."""
        return self.balance - self.frozen_balance
    
    def can_withdraw(self, amount):
        """Check if the user can withdraw the specified amount."""
        return self.available_balance >= amount
    
    def freeze_balance(self, amount):
        """Freeze a specific amount of balance."""
        if self.available_balance >= amount:
            self.frozen_balance += amount
            self.save()
            return True
        return False
    
    def unfreeze_balance(self, amount):
        """Unfreeze a specific amount of balance."""
        if self.frozen_balance >= amount:
            self.frozen_balance -= amount
            self.save()
            return True
        return False


class Transaction(models.Model):
    """
    Transaction history for wallet operations.
    """
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('trade', 'Trade'),
        ('transfer', 'Transfer'),
        ('fee', 'Fee'),
        ('reward', 'Reward'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Amount information
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    balance_before = models.DecimalField(max_digits=20, decimal_places=8)
    balance_after = models.DecimalField(max_digits=20, decimal_places=8)
    
    # Reference information
    reference_id = models.CharField(max_length=100, blank=True, null=True)  # Order ID, etc.
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount} {self.wallet.currency.symbol}"


class Deposit(models.Model):
    """
    Deposit records for users.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Deposit method (for future implementation)
    method = models.CharField(max_length=50, default='mock')
    transaction_hash = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'deposits'
        verbose_name = 'Deposit'
        verbose_name_plural = 'Deposits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency.symbol} ({self.status})"


class Withdrawal(models.Model):
    """
    Withdrawal records for users.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    net_amount = models.DecimalField(max_digits=20, decimal_places=8)  # amount - fee
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Withdrawal details
    address = models.CharField(max_length=200)  # Destination address
    transaction_hash = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'withdrawals'
        verbose_name = 'Withdrawal'
        verbose_name_plural = 'Withdrawals'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency.symbol} to {self.address}"