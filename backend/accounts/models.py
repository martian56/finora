from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model for Finora trading platform.
    Extends Django's AbstractUser to add trading-specific fields.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    
    # Trading specific fields
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Trading preferences
    trading_enabled = models.BooleanField(default=True)
    two_factor_enabled = models.BooleanField(default=False)
    
    # KYC fields (for future implementation)
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.username})"
    
    @property
    def full_name(self):
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username
    
    def get_initial_balance(self):
        """Get the initial USDT balance for new users."""
        from django.conf import settings
        return settings.DEFAULT_STARTING_BALANCE