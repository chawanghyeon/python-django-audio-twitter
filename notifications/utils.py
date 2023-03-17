from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notifications.models import Notification
from users.models import User


def send_message_to_followers(user: User, message: str) -> None:
    follower_ids = user.following.values_list("user__id", flat=True)
    notifications = [
        Notification(
            sender=user,
            recipient=follower_id,
            message=message,
        )
        for follower_id in follower_ids
    ]

    notifications = Notification.objects.bulk_create(notifications)

    channel_layer = get_channel_layer()

    for notification in notifications:
        async_to_sync(channel_layer.group_send)(
            str(notification.recipient.id),
            {
                "type": "notification_message",
                "user_id": notification.sender.id,
                "notification_id": notification.id,
            },
        )


def send_message_to_user(sender: int, recipient: int, message: str) -> None:
    notification = Notification.objects.create(
        sender_id=sender,
        recipient_id=recipient,
        message=message,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        str(notification.recipient.id),
        {
            "type": "notification_message",
            "user_id": notification.sender.id,
            "notification_id": notification.id,
        },
    )
