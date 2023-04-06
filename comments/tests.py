from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from babbles.models import Babble
from comments.models import Comment
from users.models import User


class CommentViewSetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user1_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
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

        self.comment1 = Comment.objects.create(
            user=self.user1, babble=self.babble1, audio=self.test_audio_file1
        )

        self.babble1.comment_count = 1
        self.babble1.save()

        self.comment_url = reverse("comment-list", args=[self.babble1.id])

    def test_create_comment(self):
        with open("test.mp3", "rb") as test_audio_file:
            data = {"audio": test_audio_file}
            response = self.client.post(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(user=self.user1).count(), 2)
        self.babble1.refresh_from_db()
        self.assertEqual(self.babble1.comment_count, 2)

    def test_retrieve_comments(self):
        response = self.client.get(reverse("comment-list", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["audio"],
            "http://testserver" + self.comment1.audio.url,
        )

    def test_partial_update_comment(self):
        data = {"audio": self.test_audio_file2}
        temp = self.comment1.audio
        response = self.client.patch(
            reverse("comment-detail", args=[self.babble1.id, self.comment1.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["audio"], temp.url)

    def test_destroy_comment(self):
        response = self.client.delete(
            reverse("comment-detail", args=[self.babble1.id, self.comment1.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Comment.objects.filter(id=self.comment1.id).exists())

    def test_create_comment_no_auth(self):
        self.client.credentials()
        data = {"babble": self.babble1.id, "audio": self.test_audio_file1}
        response = self.client.post(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_comments_no_auth(self):
        self.client.credentials()
        response = self.client.get(reverse("comment-list", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_comment_no_auth(self):
        self.client.credentials()
        data = {"audio": self.test_audio_file2}
        response = self.client.patch(
            reverse("comment-detail", args=[self.babble1.id, self.comment1.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_comment_no_auth(self):
        self.client.credentials()
        response = self.client.delete(
            reverse("comment-detail", args=[self.babble1.id, self.comment1.id])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
