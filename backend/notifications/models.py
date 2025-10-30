from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from markets.models import TradingPair

User = get_user_model()


class Notification(models.Model):
    """
    System notifications for users.
    """
    NOTIFICATION_TYPES = [
        ('trade', 'Trade'),
        ('order', 'Order'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('price_alert', 'Price Alert'),
        ('system', 'System'),
        ('security', 'Security'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification content
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Related objects
    trading_pair = models.ForeignKey(
        TradingPair, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Mark the notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class PriceAlert(models.Model):
    """
    Price alerts for trading pairs.
    """
    ALERT_TYPES = [
        ('above', 'Price Above'),
        ('below', 'Price Below'),
        ('change', 'Price Change'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('triggered', 'Triggered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE, related_name='price_alerts')
    
    # Alert configuration
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    target_price = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Notification settings
    notify_email = models.BooleanField(default=True)
    notify_push = models.BooleanField(default=False)
    
    # Trigger information
    triggered_at = models.DateTimeField(null=True, blank=True)
    triggered_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'price_alerts'
        verbose_name = 'Price Alert'
        verbose_name_plural = 'Price Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.trading_pair.symbol} {self.alert_type} {self.target_price}"
    
    def check_trigger(self, current_price):
        """Check if the alert should be triggered."""
        if self.status != 'active':
            return False
        
        if self.alert_type == 'above' and current_price >= self.target_price:
            return True
        elif self.alert_type == 'below' and current_price <= self.target_price:
            return True
        
        return False
    
    def trigger(self, current_price):
        """Trigger the price alert."""
        self.status = 'triggered'
        self.triggered_at = timezone.now()
        self.triggered_price = current_price
        self.save()
        
        # Create notification
        Notification.objects.create(
            user=self.user,
            notification_type='price_alert',
            title=f"Price Alert Triggered",
            message=f"{self.trading_pair.symbol} price is now {current_price} (target: {self.target_price})",
            trading_pair=self.trading_pair,
            reference_id=str(self.id)
        )