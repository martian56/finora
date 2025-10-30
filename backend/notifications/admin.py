from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Notification, PriceAlert


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model."""
    
    list_display = [
        'id', 'user', 'title', 'notification_type',
        'is_read', 'priority', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'priority', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__username', 'title', 'message'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'title', 'message', 'notification_type', 'priority')
        }),
        ('Status', {
            'fields': ('is_read', 'is_sent')
        }),
        ('Related Objects', {
            'fields': ('trading_pair', 'reference_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('user', 'trading_pair')
    
    def message_preview(self, obj):
        """Show message preview."""
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message
    message_preview.short_description = 'Message Preview'
    
    def notification_status(self, obj):
        """Show notification status with color coding."""
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Read</span>')
        else:
            return format_html('<span style="color: red;">✗ Unread</span>')
    notification_status.short_description = 'Status'
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_old_notifications']
    
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        updated = queryset.filter(is_read=False).update(is_read=True)
        self.message_user(request, f'{updated} notifications have been marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        updated = queryset.filter(is_read=True).update(is_read=False)
        self.message_user(request, f'{updated} notifications have been marked as unread.')
    mark_as_unread.short_description = 'Mark as unread'
    
    def delete_old_notifications(self, request, queryset):
        """Delete notifications older than 30 days."""
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff_date = timezone.now() - timedelta(days=30)
        old_notifications = queryset.filter(created_at__lt=cutoff_date)
        count = old_notifications.count()
        old_notifications.delete()
        
        self.message_user(request, f'{count} old notifications have been deleted.')
    delete_old_notifications.short_description = 'Delete old notifications'


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    """Admin for PriceAlert model."""
    
    list_display = [
        'id', 'user', 'trading_pair', 'alert_type',
        'target_price', 'status', 'created_at', 'triggered_at'
    ]
    list_filter = [
        'alert_type', 'status', 'trading_pair', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__username', 'trading_pair__base_currency__symbol'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'triggered_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('user', 'trading_pair', 'alert_type', 'target_price')
        }),
        ('Status', {
            'fields': ('status', 'triggered_at')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related(
            'user', 'trading_pair__base_currency', 'trading_pair__quote_currency'
        )
    
    def alert_status(self, obj):
        """Show alert status with color coding."""
        if obj.triggered_at:
            return format_html('<span style="color: orange;">✓ Triggered</span>')
        elif obj.status == 'active':
            return format_html('<span style="color: green;">● Active</span>')
        else:
            return format_html('<span style="color: gray;">○ Inactive</span>')
    alert_status.short_description = 'Status'
    
    def price_condition(self, obj):
        """Show price condition."""
        if obj.alert_type == 'above':
            return f"Price > ${obj.target_price}"
        else:
            return f"Price < ${obj.target_price}"
    price_condition.short_description = 'Condition'
    
    actions = ['activate_alerts', 'deactivate_alerts', 'trigger_alerts']
    
    def activate_alerts(self, request, queryset):
        """Activate selected price alerts."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} price alerts have been activated.')
    activate_alerts.short_description = 'Activate selected alerts'
    
    def deactivate_alerts(self, request, queryset):
        """Deactivate selected price alerts."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} price alerts have been deactivated.')
    deactivate_alerts.short_description = 'Deactivate selected alerts'
    
    def trigger_alerts(self, request, queryset):
        """Manually trigger selected alerts."""
        from django.utils import timezone
        
        updated = queryset.filter(status='active', triggered_at__isnull=True).update(
            triggered_at=timezone.now()
        )
        self.message_user(request, f'{updated} price alerts have been triggered.')
    trigger_alerts.short_description = 'Trigger selected alerts'