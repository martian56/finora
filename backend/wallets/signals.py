from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from markets.models import Currency
from .models import Wallet
from decimal import Decimal


@receiver(post_save, sender=User)
def create_user_wallets(sender, instance, created, **kwargs):
    """Create wallets for all active currencies when a new user is created."""
    if created:
        currencies = Currency.objects.filter(is_active=True)
        for currency in currencies:
            Wallet.objects.get_or_create(
                user=instance,
                currency=currency,
                defaults={
                    'balance': Decimal('0.00'),
                    'frozen_balance': Decimal('0.00')
                }
            )

