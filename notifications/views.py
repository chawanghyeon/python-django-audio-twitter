from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, serializer):
        notification = serializer.save(user=self.request.user)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(notification.user.id),
            {
                "type": "notification_message",
                "user_id": notification.user.id,
                "notification_id": notification.id,
            },
        )
