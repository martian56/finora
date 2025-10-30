from django.core.management.base import BaseCommand
from accounts.models import User
from markets.models import Currency
from wallets.models import Wallet
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fund test users with initial balances'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Fund all users',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Fund specific user by email',
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=10000.0,
            help='Amount of USDT to fund (default: 10000)',
        )

    def handle(self, *args, **options):
        amount = Decimal(str(options['amount']))
        
        # Get USDT currency
        try:
            usdt = Currency.objects.get(symbol='USDT')
        except Currency.DoesNotExist:
            self.stdout.write(self.style.ERROR('USDT currency not found'))
            return
        
        # Determine which users to fund
        if options['email']:
            users = User.objects.filter(email=options['email'])
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'User with email {options["email"]} not found'))
                return
        elif options['all']:
            users = User.objects.all()
        else:
            self.stdout.write(self.style.ERROR('Please specify --all or --email'))
            return
        
        funded_count = 0
        for user in users:
            # Get or create USDT wallet
            wallet, created = Wallet.objects.get_or_create(
                user=user,
                currency=usdt,
                defaults={'balance': amount, 'frozen_balance': Decimal('0')}
            )
            
            if not created:
                wallet.balance += amount
                wallet.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Funded {user.email} with {amount} USDT (Total: {wallet.balance} USDT)'
                )
            )
            funded_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully funded {funded_count} user(s)'
            )
        )

