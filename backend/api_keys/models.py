from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets
import string

User = get_user_model()


class APIKey(models.Model):
    """
    API keys for programmatic trading access.
    """
    PERMISSION_CHOICES = [
        ('read', 'Read Only'),
        ('trade', 'Trade'),
        ('withdraw', 'Withdraw'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    
    # Key information
    name = models.CharField(max_length=100)  # User-defined name for the key
    api_key = models.CharField(max_length=64, unique=True)
    secret_key = models.CharField(max_length=64)
    
    # Permissions
    permissions = models.JSONField(default=list)  # List of permissions
    
    # Status and limits
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_ip_restricted = models.BooleanField(default=False)
    allowed_ips = models.JSONField(default=list, blank=True)  # List of allowed IPs
    
    # Rate limiting
    requests_per_minute = models.PositiveIntegerField(default=1200)
    requests_per_day = models.PositiveIntegerField(default=100000)
    
    # Usage tracking
    last_used = models.DateTimeField(null=True, blank=True)
    request_count_today = models.PositiveIntegerField(default=0)
    request_count_minute = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = self.generate_api_key()
        if not self.secret_key:
            self.secret_key = self.generate_secret_key()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_api_key():
        """Generate a random API key."""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    @staticmethod
    def generate_secret_key():
        """Generate a random secret key."""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def is_expired(self):
        """Check if the API key is expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def is_active(self):
        """Check if the API key is active and not expired."""
        return self.status == 'active' and not self.is_expired()
    
    def can_make_request(self):
        """Check if the API key can make a request based on rate limits."""
        now = timezone.now()
        
        # Reset daily counter if it's a new day
        if self.last_used and self.last_used.date() != now.date():
            self.request_count_today = 0
        
        # Reset minute counter if it's a new minute
        if self.last_used and (now - self.last_used).seconds >= 60:
            self.request_count_minute = 0
        
        # Check rate limits
        if self.request_count_today >= self.requests_per_day:
            return False, "Daily request limit exceeded"
        
        if self.request_count_minute >= self.requests_per_minute:
            return False, "Minute request limit exceeded"
        
        return True, "OK"
    
    def record_request(self):
        """Record a successful API request."""
        now = timezone.now()
        
        # Reset counters if needed
        if self.last_used and self.last_used.date() != now.date():
            self.request_count_today = 0
        
        if self.last_used and (now - self.last_used).seconds >= 60:
            self.request_count_minute = 0
        
        # Increment counters
        self.request_count_today += 1
        self.request_count_minute += 1
        self.last_used = now
        
        self.save(update_fields=['request_count_today', 'request_count_minute', 'last_used'])
    
    def has_permission(self, permission):
        """Check if the API key has a specific permission."""
        return permission in self.permissions
    
    def revoke(self):
        """Revoke the API key."""
        self.status = 'revoked'
        self.save(update_fields=['status'])


class APIKeyUsage(models.Model):
    """
    Track API key usage for monitoring and analytics.
    """
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='usage_logs')
    
    # Request details
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)  # GET, POST, etc.
    status_code = models.PositiveIntegerField()
    response_time_ms = models.PositiveIntegerField()
    
    # Request metadata
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    
    # Error information
    error_message = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_key_usage'
        verbose_name = 'API Key Usage'
        verbose_name_plural = 'API Key Usage Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.api_key.name} - {self.method} {self.endpoint} ({self.status_code})"