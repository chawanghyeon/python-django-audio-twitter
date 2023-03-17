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
        self.follow_url = reverse("follower-list")
        self.user1_token = RefreshToken.for_user(self.user1)
        self.user2_token = RefreshToken.for_user(self.user2)

    def test_create_follower(self):
        self.client.login(username="user1", password="user1_password")
        response = self.client.post(
            self.follow_url,
            {"following": self.user2.id},
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Follower.objects.filter(user=self.user1, following=self.user2).exists()
        )

    def test_destroy_follower(self):
        follower = Follower.objects.create(user=self.user1, following=self.user2)
        self.client.login(username="user1", password="user1_password")
        response = self.client.delete(
            reverse("follower-detail", args=[self.user2.id]),
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Follower.objects.filter(user=self.user1, following=self.user2).exists()
        )

    def test_create_follower_not_authenticated(self):
        response = self.client.post(self.follow_url, {"following": self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_follower_not_authenticated(self):
        follower = Follower.objects.create(user=self.user1, following=self.user2)
        response = self.client.delete(reverse("follower-detail", args=[follower.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
