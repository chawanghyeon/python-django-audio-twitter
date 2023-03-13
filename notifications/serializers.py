from rest_framework import serializers

from notifications.models import Notification
from users.serializers import UserInSerializer


class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserInSerializer(many=False, read_only=True)
    sender = UserInSerializer(many=False, read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
