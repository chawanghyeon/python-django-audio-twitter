from channels.testing import WebsocketCommunicator
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from audiotwitter.asgi import application
from notifications.models import Notification
from users.models import User


class NotificationConsumerTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.token = str(RefreshToken.for_user(self.user1).access_token)

    async def test_connect(self):
        communicator = WebsocketCommunicator(
            application, f"ws://localhost:8000/ws/?token={self.token}"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

    async def test_disconnect(self):
        communicator = WebsocketCommunicator(
            application, f"ws://localhost:8000/ws/?token={self.token}"
        )
        await communicator.connect()
        await communicator.disconnect()

    async def test_connect_no_auth(self):
        communicator = WebsocketCommunicator(
            application, f"ws://localhost:8000/ws/?token=wrong_token"
        )
        try:
            connected, _ = await communicator.connect()
        except Exception:
            return
        self.assertFalse(connected)


class NotificationViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="user2_password"
        )
        self.notification = Notification.objects.create(
            sender=self.user2, recipient=self.user1, message="Test notification"
        )
        self.user1_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )

    def test_create_notification(self):
        response = self.client.post(reverse("notifications-list"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Notification.objects.filter(recipient=self.user1, is_read=True).exists()
        )

    def test_list_notifications(self):
        response = self.client.get(reverse("notifications-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_notification_not_authenticated(self):
        self.client.credentials()
        response = self.client.post(reverse("notifications-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notifications_not_authenticated(self):
        self.client.credentials()
        response = self.client.get(reverse("notifications-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
