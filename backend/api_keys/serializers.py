from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import APIKey, APIKeyUsage
import secrets
import string


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for APIKey model."""
    key = serializers.CharField(source='api_key', read_only=True)
    secret = serializers.CharField(source='secret_key', read_only=True)
    is_active = serializers.SerializerMethodField()
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'user', 'name', 'key', 'secret', 'permissions',
            'status', 'is_active', 'created_at', 'last_used'
        ]
        read_only_fields = ['id', 'user', 'key', 'secret', 'created_at', 'last_used', 'status']
    
    @extend_schema_field(serializers.BooleanField())
    def get_is_active(self, obj):
        """Return True if status is 'active'."""
        return obj.status == 'active'
    
    def validate_permissions(self, value):
        """Ensure permissions is a list."""
        if value is None:
            return []
        if isinstance(value, str):
            # If a single string is passed, convert to list
            return [value]
        return value
    
    def create(self, validated_data):
        """Generate API key and secret when creating."""
        # Generate random key and secret
        api_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        secret_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
        
        validated_data['api_key'] = api_key
        validated_data['secret_key'] = secret_key
        
        # Ensure permissions is a list
        if 'permissions' not in validated_data:
            validated_data['permissions'] = []
        
        # User will be set by perform_create in the ViewSet
        
        return super().create(validated_data)


class APIKeyUsageSerializer(serializers.ModelSerializer):
    """Serializer for APIKeyUsage model."""
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    
    class Meta:
        model = APIKeyUsage
        fields = [
            'id', 'api_key', 'api_key_name', 'endpoint', 'method', 
            'status_code', 'response_time_ms', 'ip_address', 'user_agent',
            'error_message', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
