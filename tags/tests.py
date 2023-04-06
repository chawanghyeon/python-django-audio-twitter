from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from babbles.models import Babble
from babbles.serializers import BabbleSerializer
from tags.models import Tag
from users.models import User


class TagViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = self.client
        self.user = User.objects.create_user(username="user", password="user_password")
        self.tag = Tag.objects.create(text="testtag")
        self.babble = Babble.objects.create(user=self.user)
        self.babble.tags.add(self.tag)
        self.babble.save()
        self.token = str(RefreshToken.for_user(self.user).access_token)

    def test_retrieve_tag(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(reverse("tags-detail", args=[self.tag.text]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        serializer = BabbleSerializer(self.babble)
        serialized_data = [serializer.data]

        self.assertEqual(response.data["results"], serialized_data)

    def test_retrieve_tag_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(reverse("tags-detail", args=["notfound"]))

        self.assertEqual(len(response.data["results"]), 0)

    def test_retrieve_tag_no_auth(self):
        response = self.client.get(reverse("tags-detail", args=[self.tag.text]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_tag_not_found_no_auth(self):
        response = self.client.get(reverse("tags-detail", args=[self.tag.text]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
