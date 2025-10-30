from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with enhanced functionality."""
    
    list_display = [
        'email', 'username', 'first_name', 'last_name', 
        'is_verified', 'trading_enabled', 'kyc_status', 
        'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_verified', 'trading_enabled', 'kyc_status', 
        'is_active', 'is_staff', 'is_superuser', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'username', 'first_name', 'last_name')
        }),
        ('Trading Status', {
            'fields': ('is_verified', 'trading_enabled', 'kyc_status'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Account Information', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
        ('Permissions', {
            'classes': ('wide',),
            'fields': ('is_active', 'is_staff', 'is_verified', 'trading_enabled'),
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return super().get_queryset(request).select_related()
    
    def trading_status(self, obj):
        """Display trading status with color coding."""
        if obj.trading_enabled and obj.is_verified:
            return format_html('<span style="color: green;">✓ Active</span>')
        elif obj.trading_enabled:
            return format_html('<span style="color: orange;">⚠ Pending Verification</span>')
        else:
            return format_html('<span style="color: red;">✗ Disabled</span>')
    trading_status.short_description = 'Trading Status'
    
    actions = ['enable_trading', 'disable_trading', 'verify_users']
    
    def enable_trading(self, request, queryset):
        """Enable trading for selected users."""
        updated = queryset.update(trading_enabled=True)
        self.message_user(request, f'{updated} users have been enabled for trading.')
    enable_trading.short_description = 'Enable trading for selected users'
    
    def disable_trading(self, request, queryset):
        """Disable trading for selected users."""
        updated = queryset.update(trading_enabled=False)
        self.message_user(request, f'{updated} users have been disabled from trading.')
    disable_trading.short_description = 'Disable trading for selected users'
    
    def verify_users(self, request, queryset):
        """Verify selected users."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users have been verified.')
    verify_users.short_description = 'Verify selected users'