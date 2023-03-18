from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from babbles.models import Babble
from likes.models import Like
from users.models import User


class LikeViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="user2_password"
        )
        self.babble = Babble.objects.create(user=self.user2, content="Test babble")
        self.client.force_authenticate(user=self.user1)

    def test_create_like(self):
        response = self.client.post(reverse("like-list"), {"babble": self.babble.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Like.objects.filter(user=self.user1, babble=self.babble).exists()
        )

    def test_destroy_like(self):
        like = Like.objects.create(user=self.user1, babble=self.babble)
        response = self.client.delete(reverse("like-detail", args=[like.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Like.objects.filter(user=self.user1, babble=self.babble).exists()
        )

    def test_retrieve_likes(self):
        like = Like.objects.create(user=self.user1, babble=self.babble)
        response = self.client.get(reverse("like-retrieve", args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_like_not_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse("like-list"), {"babble": self.babble.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_like_not_authenticated(self):
        like = Like.objects.create(user=self.user1, babble=self.babble)
        self.client.force_authenticate(user=None)
        response = self.client.delete(reverse("like-detail", args=[like.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_likes_not_authenticated(self):
        like = Like.objects.create(user=self.user1, babble=self.babble)
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("like-retrieve", args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
