import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import Notification

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_add(str(user.id), self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_discard(str(user.id), self.channel_name)

    async def notification_message(self, event):
        event["user_id"]
        notification_id = event["notification_id"]
        notification = await sync_to_async(Notification.objects.get)(id=notification_id)
        message = {"id": notification.id, "message": notification.message}
        await self.send(text_data=json.dumps(message))
