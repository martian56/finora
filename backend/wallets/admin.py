from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Wallet, Transaction, Deposit, Withdrawal


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Admin for Wallet model."""
    
    list_display = [
        'user', 'currency', 'balance', 'frozen_balance',
        'available_balance', 'total_value', 'created_at'
    ]
    list_filter = ['currency', 'created_at']
    search_fields = ['user__email', 'user__username', 'currency__symbol']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Wallet Information', {
            'fields': ('user', 'currency')
        }),
        ('Balances', {
            'fields': ('balance', 'frozen_balance')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('user', 'currency')
    
    def total_value(self, obj):
        """Calculate total wallet value."""
        # In a real app, this would use current market prices
        return f"${obj.balance:.2f}"
    total_value.short_description = 'Total Value'
    
    actions = ['reset_balances']
    
    def reset_balances(self, request, queryset):
        """Reset balances to zero (for testing)."""
        updated = queryset.update(
            balance=0, frozen_balance=0
        )
        self.message_user(request, f'{updated} wallet balances have been reset.')
    reset_balances.short_description = 'Reset balances to zero'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin for Transaction model."""
    
    list_display = [
        'id', 'user', 'wallet', 'transaction_type', 'amount',
        'balance_after', 'description', 'created_at'
    ]
    list_filter = [
        'transaction_type', 'wallet__currency', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__username', 'wallet__currency__symbol',
        'description'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('user', 'wallet', 'transaction_type')
        }),
        ('Transaction Details', {
            'fields': ('amount', 'balance_after', 'description', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'user', 'wallet__currency'
        )
    
    def transaction_value(self, obj):
        """Display transaction value with type indicator."""
        if obj.transaction_type in ['deposit', 'buy']:
            return format_html('<span style="color: green;">+{:.2f}</span>', obj.amount)
        else:
            return format_html('<span style="color: red;">-{:.2f}</span>', obj.amount)
    transaction_value.short_description = 'Value'


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    """Admin for Deposit model."""
    
    list_display = [
        'id', 'user', 'currency', 'amount', 'method',
        'status', 'transaction_hash', 'created_at'
    ]
    list_filter = ['method', 'status', 'currency', 'created_at']
    search_fields = [
        'user__email', 'user__username', 'currency__symbol',
        'transaction_hash'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Deposit Information', {
            'fields': ('user', 'currency', 'amount', 'method')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'transaction_hash')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'user', 'currency'
        )
    
    actions = ['approve_deposits', 'reject_deposits']
    
    def approve_deposits(self, request, queryset):
        """Approve selected deposits."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='completed', completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} deposits have been approved.')
    approve_deposits.short_description = 'Approve selected deposits'
    
    def reject_deposits(self, request, queryset):
        """Reject selected deposits."""
        updated = queryset.filter(status='pending').update(status='failed')
        self.message_user(request, f'{updated} deposits have been rejected.')
    reject_deposits.short_description = 'Reject selected deposits'


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    """Admin for Withdrawal model."""
    
    list_display = [
        'id', 'user', 'currency', 'amount', 'address',
        'status', 'transaction_hash', 'created_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = [
        'user__email', 'user__username', 'currency__symbol',
        'address', 'transaction_hash'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Withdrawal Information', {
            'fields': ('user', 'currency', 'amount', 'address')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'transaction_hash')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'user', 'currency'
        )
    
    actions = ['approve_withdrawals', 'reject_withdrawals']
    
    def approve_withdrawals(self, request, queryset):
        """Approve selected withdrawals."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='completed', completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} withdrawals have been approved.')
    approve_withdrawals.short_description = 'Approve selected withdrawals'
    
    def reject_withdrawals(self, request, queryset):
        """Reject selected withdrawals."""
        updated = queryset.filter(status='pending').update(status='failed')
        self.message_user(request, f'{updated} withdrawals have been rejected.')
    reject_withdrawals.short_description = 'Reject selected withdrawals'