from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Babble, Rebabble


class RebabbleViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword2"
        )
        self.babble = Babble.objects.create(
            content="Test babble content", user=self.user2
        )
        self.client.force_authenticate(user=self.user)

    def test_create_rebabble(self):
        response = self.client.post(
            reverse("rebabble-create"),
            data={"babble": self.babble.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rebabble.objects.count(), 1)

    def test_destroy_rebabble(self):
        rebabble = Rebabble.objects.create(user=self.user, babble=self.babble)
        response = self.client.delete(reverse("rebabble-destroy", args=[rebabble.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Rebabble.objects.count(), 0)

    def test_retrieve_rebabbles(self):
        Rebabble.objects.create(user=self.user, babble=self.babble)
        response = self.client.get(reverse("rebabble-retrieve", args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.babble.id)

    def test_create_rebabble_no_auth(self):
        response = self.client.post(
            reverse("rebabble-create"),
            data={"babble": self.babble.id},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Rebabble.objects.count(), 0)

    def test_destroy_rebabble_no_auth(self):
        rebabble = Rebabble.objects.create(user=self.user, babble=self.babble)
        response = self.client.delete(reverse("rebabble-destroy", args=[rebabble.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Rebabble.objects.count(), 1)

    def test_retrieve_rebabbles_no_auth(self):
        Rebabble.objects.create(user=self.user, babble=self.babble)
        response = self.client.get(reverse("rebabble-retrieve", args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
