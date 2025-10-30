from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Notification, PriceAlert
from .serializers import NotificationSerializer, PriceAlertSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model."""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})


class PriceAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for PriceAlert model."""
    queryset = PriceAlert.objects.all()
    serializer_class = PriceAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate price alert."""
        alert = self.get_object()
        alert.is_active = True
        alert.save()
        return Response({'message': 'Price alert activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate price alert."""
        alert = self.get_object()
        alert.is_active = False
        alert.save()
        return Response({'message': 'Price alert deactivated'})


class MarkNotificationReadView(APIView):
    """Mark a notification as read."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id, 
                user=request.user
            )
            notification.mark_as_read()
            return Response({'message': 'Notification marked as read'})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class MarkAllNotificationsReadView(APIView):
    """Mark all notifications as read."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})


class UnreadNotificationCountView(APIView):
    """Get unread notification count."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        return Response({'unread_count': count})


class CreatePriceAlertView(APIView):
    """Create a price alert."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PriceAlertSerializer(data=request.data)
        if serializer.is_valid():
            alert = serializer.save(user=request.user)
            return Response(PriceAlertSerializer(alert).data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelPriceAlertView(APIView):
    """Cancel a price alert."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, alert_id):
        try:
            alert = PriceAlert.objects.get(id=alert_id, user=request.user)
            alert.status = 'cancelled'
            alert.save()
            return Response({'message': 'Price alert cancelled successfully'})
        except PriceAlert.DoesNotExist:
            return Response({'error': 'Price alert not found'}, 
                          status=status.HTTP_404_NOT_FOUND)