from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from babbles.models import Babble
from users.models import User
from users.serializers import UserSerializer


class UserViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="user2_password"
        )

        self.babble = Babble.objects.create(user=self.user1)
        self.user1_token = RefreshToken.for_user(self.user1)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )

    def test_retrieve_user(self):
        response = self.client.get(reverse("users-detail", args=[self.user1.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = UserSerializer(self.user1)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_user_no_auth(self):
        self.client.credentials()
        response = self.client.get(reverse("users-detail", args=[self.user1.id]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_user(self):
        response = self.client.patch(
            reverse("users-detail", args=[self.user1.id]),
            {"first_name": "NewFirstName"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "NewFirstName")

    def test_partial_update_user_no_auth(self):
        self.client.credentials()
        response = self.client.patch(
            reverse("users-detail", args=[self.user1.id]),
            {"first_name": "NewFirstName"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_user(self):
        response = self.client.delete(
            reverse("users-detail", args=[self.user1.id]),
            {"password": "user1_password"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_destroy_user_wrong_password(self):
        response = self.client.delete(
            reverse("users-detail", args=[self.user1.id]), {"password": "wrongpassword"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_user_no_auth(self):
        self.client.credentials()
        response = self.client.delete(
            reverse("users-detail", args=[self.user1.id]),
            {"password": "user1_password"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_password(self):
        response = self.client.patch(
            reverse("users-password"),
            {"old_password": "user1_password", "new_password": "newpassword"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.check_password("newpassword"))

    def test_update_password_wrong_old_password(self):
        response = self.client.patch(
            reverse("users-password"),
            {"old_password": "wrongpassword", "new_password": "newpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
