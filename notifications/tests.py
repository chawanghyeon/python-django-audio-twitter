from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
from django.test import AsyncTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from audiotwitter.asgi import application
from notifications.models import Notification
from users.models import User


class NotificationConsumerTestCase(AsyncTestCase):
    async def setUp(self):
        self.user = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.communicator = WebsocketCommunicator(application, "/ws/notifications/")
        self.communicator.scope["user"] = self.user

    async def test_connect_authenticated(self):
        connected, _ = await self.communicator.connect()
        self.assertTrue(connected)

    async def test_disconnect(self):
        await self.communicator.connect()
        await self.communicator.disconnect()

    async def test_receive(self):
        await self.communicator.connect()
        message = {"message": "Test message"}
        await self.communicator.send_json_to(message)
        event = await self.communicator.receive_json_from()
        self.assertEqual(event["type"], "notification.message")
        self.assertEqual(event["message"], message["message"])

    async def test_connect_not_authenticated(self):
        self.communicator.scope["user"] = AnonymousUser()
        connected, _ = await self.communicator.connect()
        self.assertFalse(connected)


class NotificationViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="user2_password"
        )
        self.client.force_authenticate(user=self.user1)
        self.notification = Notification.objects.create(
            sender=self.user2, recipient=self.user1, message="Test notification"
        )

    def test_create_notification(self):
        response = self.client.post(reverse("notification-list"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Notification.objects.filter(recipient=self.user1, is_read=True).exists()
        )

    def test_list_notifications(self):
        response = self.client.get(reverse("notification-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_notification_not_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse("notification-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notifications_not_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("notification-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
