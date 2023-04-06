from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from babbles.models import Babble
from rebabbles.models import Rebabble
from users.models import User


class RebabbleViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.babble = Babble.objects.create(user=self.user1)
        self.token = str(RefreshToken.for_user(self.user1).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_rebabble(self):
        response = self.client.post(reverse("rebabbles", args=[self.babble.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rebabble.objects.count(), 1)
        self.babble.refresh_from_db()
        self.assertEqual(self.babble.rebabble_count, 1)

    def test_destroy_rebabble(self):
        Rebabble.objects.create(user=self.user1, babble=self.babble)
        self.babble.rebabble_count = 1
        self.babble.save()
        response = self.client.delete(reverse("rebabbles", args=[self.babble.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Rebabble.objects.count(), 0)
        self.babble.refresh_from_db()
        self.assertEqual(self.babble.rebabble_count, 0)

    def test_retrieve_rebabbles(self):
        Rebabble.objects.create(user=self.user1, babble=self.babble)
        response = self.client.get(reverse("rebabbles_user", args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.babble.id)

    def test_create_rebabble_no_auth(self):
        self.client.credentials()
        response = self.client.post(reverse("rebabbles", args=[self.babble.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Rebabble.objects.count(), 0)

    def test_destroy_rebabble_no_auth(self):
        self.client.credentials()
        rebabble = Rebabble.objects.create(user=self.user1, babble=self.babble)
        response = self.client.delete(reverse("rebabbles", args=[rebabble.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Rebabble.objects.count(), 1)

    def test_retrieve_rebabbles_no_auth(self):
        self.client.credentials()
        Rebabble.objects.create(user=self.user1, babble=self.babble)
        response = self.client.get(reverse("rebabbles_user", args=[self.user1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
