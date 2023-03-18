from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from babbles.models import Babble
from users.models import User


class BabbleViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="user2_password"
        )

        self.babble1 = Babble.objects.create(user=self.user1, content="Test babble 1")
        self.babble2 = Babble.objects.create(user=self.user2, content="Test babble 2")

        self.babble_url = reverse(
            "babble-list"
        )  # Replace with the actual viewset name in your project

        self.user1_token = RefreshToken.for_user(self.user1)
        self.user2_token = RefreshToken.for_user(self.user2)

    def test_create_babble(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.post(self.babble_url, {"content": "New babble"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Babble.objects.filter(user=self.user1, content="New babble").exists()
        )

    def test_retrieve_babble(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.get(reverse("babble-detail", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], self.babble1.content)

    def test_update_babble(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.patch(
            reverse("babble-detail", args=[self.babble1.id]),
            {"content": "Updated babble"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.babble1.refresh_from_db()
        self.assertEqual(self.babble1.content, "Updated babble")

    def test_destroy_babble(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.delete(reverse("babble-detail", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Babble.objects.filter(id=self.babble1.id).exists())

    def test_list_babbles(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.get(self.babble_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_explore_babbles(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.get(reverse("babble-explore"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 1
        )  # user1 should not see their own babbles

    def test_profile_babbles(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.get(reverse("babble-profile", args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # user2 has only one babble
