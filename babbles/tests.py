from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from babbles.models import Babble
from followers.models import Follower
from users.models import User


class BabbleViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="user2_password"
        )
        with open("test.mp3", "rb") as f:
            test_audio_file_content = f.read()

        self.test_audio_file1 = SimpleUploadedFile(
            "test1.mp3", test_audio_file_content, content_type="audio/mp3"
        )
        self.test_audio_file2 = SimpleUploadedFile(
            "test2.mp3", test_audio_file_content, content_type="audio/mp3"
        )
        self.babble1 = Babble.objects.create(
            user=self.user1, audio=self.test_audio_file1
        )
        self.babble2 = Babble.objects.create(
            user=self.user2, audio=self.test_audio_file1
        )

        self.babble_url = reverse("babbles-list")

        self.user1_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )

    def test_create_babble(self):
        with open("test.mp3", "rb") as test_audio_file:
            response = self.client.post(
                self.babble_url, {"audio": test_audio_file}, format="multipart"
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Babble.objects.filter(user=self.user1).exclude(audio="").exists()
        )

    def test_retrieve_babble(self):
        response = self.client.get(reverse("babbles-detail", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["audio"], self.babble1.audio.url)

    def test_partial_update_babble(self):
        temp = self.babble1.audio
        response = self.client.patch(
            reverse("babbles-detail", args=[self.babble1.id]),
            {"audio": self.test_audio_file2},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.babble1.refresh_from_db()
        self.assertNotEqual(self.babble1.audio, temp)

    def test_destroy_babble(self):
        response = self.client.delete(reverse("babbles-detail", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Babble.objects.filter(id=self.babble1.id).exists())

    def test_list_babbles1(self):
        Follower.objects.create(user=self.user1, following=self.user2)
        response = self.client.get(self.babble_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_babbles2(self):
        response = self.client.get(self.babble_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_explore_babbles(self):
        response = self.client.get(reverse("babbles-explore"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_profile_babbles(self):
        response = self.client.get(reverse("babbles-profile", args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_babble_no_auth(self):
        self.client.credentials()
        response = self.client.post(self.babble_url, {"content": "New babble"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_babble_no_auth(self):
        self.client.credentials()
        response = self.client.get(reverse("babbles-detail", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_babble_no_auth(self):
        self.client.credentials()
        response = self.client.patch(
            reverse("babbles-detail", args=[self.babble1.id]),
            {"content": "Updated babble"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_babble_no_auth(self):
        self.client.credentials()
        response = self.client.delete(reverse("babbles-detail", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_babbles_no_auth(self):
        self.client.credentials()
        response = self.client.get(self.babble_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_explore_babbles_no_auth(self):
        self.client.credentials()
        response = self.client.get(reverse("babbles-explore"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_babbles_no_auth(self):
        self.client.credentials()
        response = self.client.get(reverse("babbles-profile", args=[self.user2.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
