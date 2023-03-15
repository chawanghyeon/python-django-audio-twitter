import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from notifications.models import Notification
from users.models import User

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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            "notifications", {"type": "notification.message", "message": message}
        )

    async def notification_message(self, event):
        notification_id = event["notification_id"]
        notification = await Notification.objects.select_related().aget(
            id=notification_id
        )
        splited_message = list(notification.message.split(" "))

        sender = {
            "id": notification.sender.id,
            "nickname": notification.sender.nickname,
            "first_name": notification.sender.first_name,
            "last_name": notification.sender.last_name,
        }

        recipient = {
            "id": notification.recipient.id,
            "nickname": notification.recipient.nickname,
            "first_name": notification.recipient.first_name,
            "last_name": notification.recipient.last_name,
        }

        if notification.sender.image:
            sender["image"] = notification.sender.image.url
        if notification.recipient.image:
            recipient["image"] = notification.recipient.image.url
        if notification.sender.background:
            sender["background"] = notification.sender.background.url
        if notification.recipient.background:
            recipient["background"] = notification.recipient.background.url

        message = {
            "id": notification.id,
            "message": notification.message,
            "sender": sender,
            "recipient": recipient,
        }

        if "babble" in notification.message:
            message["babble_id"] = splited_message[-1]

        await self.send(text_data=json.dumps(message))
