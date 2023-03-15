from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notifications.models import Notification
from users.models import User


def send_message_to_followers(user: User, message: str) -> None:
    followers = user.following.all()
    notifications = [
        Notification(
            sender=user,
            recipient=follower.user,
            message=message,
        )
        for follower in followers
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


def send_message_to_user(sender: User, recipient: User, message: str) -> None:
    notification = Notification.objects.create(
        sender=sender,
        recipient=recipient,
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
