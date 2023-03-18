from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Babble, Tag, User
from .serializers import BabbleSerializer


class TagViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = self.client
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.tag = Tag.objects.create(text="testtag")
        self.babble = Babble.objects.create(
            user=self.user, content="Test babble content"
        )
        self.babble.tags.add(self.tag)
        self.babble.save()

    def test_retrieve_tag(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("tag-detail", kwargs={"pk": self.tag.text})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        serializer = BabbleSerializer(self.babble)
        serialized_data = [serializer.data]

        self.assertEqual(response.data["results"], serialized_data)

    def test_retrieve_tag_not_found(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("tag-detail", kwargs={"pk": "nonexistenttag"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_tag_no_auth(self):
        url = reverse("tag-detail", kwargs={"pk": self.tag.text})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        serializer = BabbleSerializer(self.babble)
        serialized_data = [serializer.data]

        self.assertEqual(response.data["results"], serialized_data)

    def test_retrieve_tag_not_found_no_auth(self):
        url = reverse("tag-detail", kwargs={"pk": "nonexistenttag"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
