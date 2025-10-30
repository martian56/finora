from rest_framework import serializers
from .models import Wallet, Transaction, Deposit, Withdrawal
from markets.serializers import CurrencySerializer


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet model."""
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.IntegerField(write_only=True)
    available_balance = serializers.ReadOnlyField()
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'currency', 'currency_id', 'balance',
            'frozen_balance', 'available_balance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'available_balance', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""
    wallet = WalletSerializer(read_only=True)
    wallet_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'wallet', 'wallet_id', 'transaction_type',
            'status', 'amount', 'balance_before', 'balance_after',
            'reference_id', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class DepositSerializer(serializers.ModelSerializer):
    """Serializer for Deposit model."""
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Deposit
        fields = [
            'id', 'user', 'currency', 'currency_id', 'amount', 'method',
            'status', 'transaction_hash', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'completed_at']


class WithdrawalSerializer(serializers.ModelSerializer):
    """Serializer for Withdrawal model."""
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Withdrawal
        fields = [
            'id', 'user', 'currency', 'currency_id', 'amount', 'address',
            'status', 'transaction_hash', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'completed_at']
