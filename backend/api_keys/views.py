from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import APIKey, APIKeyUsage
from .serializers import APIKeySerializer, APIKeyUsageSerializer


class APIKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for APIKey model."""
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate API key secret."""
        api_key = self.get_object()
        # Generate new secret
        import secrets
        import string
        new_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
        api_key.secret = new_secret
        api_key.save()
        return Response({'message': 'API key secret regenerated successfully'})


class APIKeyUsageViewSet(viewsets.ModelViewSet):
    """ViewSet for APIKeyUsage model."""
    queryset = APIKeyUsage.objects.all()
    serializer_class = APIKeyUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIKeyUsage.objects.filter(api_key__user=self.request.user).select_related('api_key')


class CreateAPIKeyView(APIView):
    """Create a new API key."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = APIKeySerializer(data=request.data)
        if serializer.is_valid():
            api_key = serializer.save(user=request.user)
            return Response({
                'api_key': api_key.api_key,
                'secret_key': api_key.secret_key,
                'data': APIKeySerializer(api_key).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RevokeAPIKeyView(APIView):
    """Revoke an API key."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, key_id):
        try:
            api_key = APIKey.objects.get(id=key_id, user=request.user)
            api_key.revoke()
            return Response({'message': 'API key revoked successfully'})
        except APIKey.DoesNotExist:
            return Response({'error': 'API key not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class APIKeyUsageView(APIView):
    """Get API key usage statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, key_id):
        try:
            api_key = APIKey.objects.get(id=key_id, user=request.user)
            usage_logs = APIKeyUsage.objects.filter(api_key=api_key)
            serializer = APIKeyUsageSerializer(usage_logs, many=True)
            return Response(serializer.data)
        except APIKey.DoesNotExist:
            return Response({'error': 'API key not found'}, 
                          status=status.HTTP_404_NOT_FOUND)