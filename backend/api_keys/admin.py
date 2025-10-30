from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import APIKey, APIKeyUsage


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin for APIKey model."""
    
    list_display = [
        'id', 'user', 'name', 'api_key_preview', 'permissions_display',
        'status', 'last_used', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'last_used']
    search_fields = ['user__email', 'user__username', 'name', 'api_key']
    ordering = ['-created_at']
    readonly_fields = ['api_key', 'secret_key', 'created_at', 'last_used']
    
    fieldsets = (
        ('API Key Information', {
            'fields': ('user', 'name', 'status')
        }),
        ('Credentials', {
            'fields': ('api_key', 'secret_key'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'classes': ('collapse',)
        }),
        ('Security Settings', {
            'fields': ('is_ip_restricted', 'allowed_ips'),
            'classes': ('collapse',)
        }),
        ('Rate Limiting', {
            'fields': ('requests_per_minute', 'requests_per_day'),
            'classes': ('collapse',)
        }),
        ('Usage Information', {
            'fields': ('last_used', 'request_count_today', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('user')
    
    def api_key_preview(self, obj):
        """Show partial API key for security."""
        if obj.api_key:
            return f"{obj.api_key[:8]}...{obj.api_key[-4:]}"
        return "N/A"
    api_key_preview.short_description = 'API Key'
    
    def permissions_display(self, obj):
        """Display permissions as badges."""
        if obj.permissions:
            badges = []
            for permission in obj.permissions:
                badges.append(f'<span style="background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{permission}</span>')
            return format_html(' '.join(badges))
        return "No permissions"
    permissions_display.short_description = 'Permissions'
    
    def usage_status(self, obj):
        """Show usage status."""
        if obj.last_used:
            days_since = (timezone.now() - obj.last_used).days
            if days_since < 7:
                return format_html('<span style="color: green;">Active</span>')
            elif days_since < 30:
                return format_html('<span style="color: orange;">Inactive</span>')
            else:
                return format_html('<span style="color: red;">Dormant</span>')
        return format_html('<span style="color: gray;">Never used</span>')
    usage_status.short_description = 'Usage Status'
    
    actions = ['activate_keys', 'deactivate_keys', 'regenerate_secrets']
    
    def activate_keys(self, request, queryset):
        """Activate selected API keys."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} API keys have been activated.')
    activate_keys.short_description = 'Activate selected API keys'
    
    def deactivate_keys(self, request, queryset):
        """Deactivate selected API keys."""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} API keys have been deactivated.')
    deactivate_keys.short_description = 'Deactivate selected API keys'
    
    def regenerate_secrets(self, request, queryset):
        """Regenerate secrets for selected API keys."""
        import secrets
        import string
        
        updated = 0
        for api_key in queryset:
            new_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
            api_key.secret_key = new_secret
            api_key.save()
            updated += 1
        
        self.message_user(request, f'{updated} API key secrets have been regenerated.')
    regenerate_secrets.short_description = 'Regenerate secrets for selected API keys'


@admin.register(APIKeyUsage)
class APIKeyUsageAdmin(admin.ModelAdmin):
    """Admin for APIKeyUsage model."""
    
    list_display = [
        'id', 'api_key', 'endpoint', 'method', 'status_code',
        'response_time_ms', 'timestamp'
    ]
    list_filter = [
        'method', 'status_code', 'endpoint', 'timestamp'
    ]
    search_fields = [
        'api_key__user__email', 'api_key__name', 'endpoint'
    ]
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('api_key', 'endpoint', 'method')
        }),
        ('Response Details', {
            'fields': ('status_code', 'response_time_ms', 'timestamp')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('api_key__user')
    
    def status_display(self, obj):
        """Display status code with color coding."""
        if 200 <= obj.status_code < 300:
            return format_html('<span style="color: green;">{}</span>', obj.status_code)
        elif 400 <= obj.status_code < 500:
            return format_html('<span style="color: orange;">{}</span>', obj.status_code)
        elif obj.status_code >= 500:
            return format_html('<span style="color: red;">{}</span>', obj.status_code)
        else:
            return str(obj.status_code)
    status_display.short_description = 'Status'
    
    def response_time_display(self, obj):
        """Display response time with color coding."""
        if obj.response_time_ms < 100:
            return format_html('<span style="color: green;">{}ms</span>', obj.response_time_ms)
        elif obj.response_time_ms < 500:
            return format_html('<span style="color: orange;">{}ms</span>', obj.response_time_ms)
        else:
            return format_html('<span style="color: red;">{}ms</span>', obj.response_time_ms)
    response_time_display.short_description = 'Response Time'
    
    # Add custom actions for usage analysis
    actions = ['analyze_slow_requests', 'analyze_error_requests']
    
    def analyze_slow_requests(self, request, queryset):
        """Analyze slow requests."""
        slow_requests = queryset.filter(response_time_ms__gt=1000).count()
        self.message_user(request, f'Found {slow_requests} requests slower than 1 second.')
    analyze_slow_requests.short_description = 'Analyze slow requests'
    
    def analyze_error_requests(self, request, queryset):
        """Analyze error requests."""
        error_requests = queryset.filter(status_code__gte=400).count()
        self.message_user(request, f'Found {error_requests} error requests.')
    analyze_error_requests.short_description = 'Analyze error requests'