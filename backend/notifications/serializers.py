from rest_framework import serializers
from .models import Notification, PriceAlert


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class PriceAlertSerializer(serializers.ModelSerializer):
    """Serializer for PriceAlert model."""
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceAlert
        fields = [
            'id', 'user', 'trading_pair', 'alert_type', 'target_price',
            'status', 'is_active', 'created_at', 'triggered_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'triggered_at']
    
    def get_is_active(self, obj):
        """Return True if status is 'active'."""
        return obj.status == 'active'
