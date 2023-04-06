# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from followers.models import Follower
from users.models import User


class FollowerViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="user2_password"
        )

        self.user1_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )

    def test_create_follower(self):
        response = self.client.post(reverse("followers", args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Follower.objects.filter(user=self.user1, following=self.user2).exists()
        )
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.following_count, 1)
        self.assertEqual(self.user2.follower_count, 1)

    def test_destroy_follower(self):
        self.test_create_follower()
        response = self.client.delete(reverse("followers", args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Follower.objects.filter(user=self.user1, following=self.user2).exists()
        )
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.following_count, 0)
        self.assertEqual(self.user2.follower_count, 0)

    def test_create_follower_no_auth(self):
        self.client.credentials()
        response = self.client.post(reverse("followers", args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_follower_no_auth(self):
        self.client.credentials()
        Follower.objects.create(user=self.user1, following=self.user2)
        response = self.client.delete(reverse("followers", args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
