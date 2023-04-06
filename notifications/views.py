from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, request: HttpRequest) -> Response:
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True
        )

        return Response(status=status.HTTP_201_CREATED)

    def list(self, request: HttpRequest) -> Response:
        queryset = Notification.objects.filter(
            recipient=self.request.user, is_read=False
        ).order_by("-created")
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
