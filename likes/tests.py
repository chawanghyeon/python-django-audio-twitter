from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from babbles.models import Babble
from likes.models import Like
from users.models import User


class LikeViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.babble = Babble.objects.create(user=self.user1)
        self.user1_token = RefreshToken.for_user(self.user1)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )

    def test_create_like(self):
        response = self.client.post(reverse("likes", args=[self.babble.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Like.objects.filter(user=self.user1, babble=self.babble).exists()
        )
        self.babble.refresh_from_db()
        self.assertEqual(self.babble.like_count, 1)

    def test_destroy_like(self):
        Like.objects.create(user=self.user1, babble=self.babble)
        self.babble.like_count = 1
        self.babble.save()
        response = self.client.delete(reverse("likes", args=[self.babble.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Like.objects.filter(user=self.user1, babble=self.babble).exists()
        )
        self.babble.refresh_from_db()
        self.assertEqual(self.babble.like_count, 0)

    def test_retrieve_likes(self):
        Like.objects.create(user=self.user1, babble=self.babble)
        response = self.client.get(reverse("likes_user", args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_like_no_auth(self):
        self.client.credentials()
        response = self.client.post(reverse("likes", args=[self.babble.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_like_no_auth(self):
        Like.objects.create(user=self.user1, babble=self.babble)
        self.client.credentials()
        response = self.client.delete(reverse("likes", args=[self.babble.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_likes_no_auth(self):
        Like.objects.create(user=self.user1, babble=self.babble)
        self.client.credentials()
        response = self.client.get(reverse("likes", args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
