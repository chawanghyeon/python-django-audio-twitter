from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import User


class AuthViewSetTestCase(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser@test.com",
            "password": "testuserpassword",
        }

    def test_signup(self):
        response = self.client.post(reverse("auth-signup"), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(username=self.user_data["username"]).exists()
        )

    def test_signin(self):
        User.objects.create_user(**self.user_data)
        signin_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        response = self.client.post(reverse("auth-signin"), signin_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("access", response.data["token"])
        self.assertIn("refresh", response.data["token"])

    def test_signin_wrong_credentials(self):
        User.objects.create_user(**self.user_data)
        signin_data = {
            "username": self.user_data["username"],
            "password": "wrongpassword",
        }
        response = self.client.post(reverse("auth-signin"), signin_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
