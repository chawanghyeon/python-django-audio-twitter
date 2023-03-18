from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from babbles.models import Babble
from users.serializers import UserSerializer


class UserViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.another_user = User.objects.create_user(
            username="anotheruser", password="anotherpassword"
        )

        self.babble = Babble.objects.create(
            user=self.user, content="Test babble content"
        )

    def test_retrieve_user(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = UserSerializer(self.user)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_user_no_auth(self):
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_user(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        data = {"first_name": "NewFirstName"}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewFirstName")

    def test_partial_update_user_no_auth(self):
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        data = {"first_name": "NewFirstName"}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_user(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        data = {"password": "testpassword"}
        response = self.client.delete(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_destroy_user_wrong_password(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        data = {"password": "wrongpassword"}
        response = self.client.delete(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_user_no_auth(self):
        url = reverse("user-detail", kwargs={"pk": self.user.id})
        data = {"password": "testpassword"}
        response = self.client.delete(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_password(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("user-password", kwargs={"pk": self.user.id})
        data = {"old_password": "testpassword", "new_password": "newpassword"}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password("newpassword"))

    def test_update_password_wrong_old_password(self):
        self.client.login(username="testuser", password="testpassword")
