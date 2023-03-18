from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from babbles.models import Babble
from comments.models import Comment


class CommentViewSetTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username="user1", password="user1_password"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="user2_password"
        )

        # Create babbles
        self.babble1 = Babble.objects.create(user=self.user1, content="Babble1 content")
        self.babble2 = Babble.objects.create(user=self.user2, content="Babble2 content")

        # Create comments
        self.comment1 = Comment.objects.create(
            user=self.user1, babble=self.babble1, content="Comment1 content"
        )

        # Generate tokens for authentication
        self.user1_token = self.generate_token(self.user1)
        self.user2_token = self.generate_token(self.user2)

        # Set up comment URL
        self.comment_url = reverse("comment-list")

        self.user1_token = RefreshToken.for_user(self.user1)
        self.user2_token = RefreshToken.for_user(self.user2)

    # Add the generate_token function here (from previous examples)

    def test_create_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        data = {"babble": self.babble1.id, "content": "New comment"}
        response = self.client.post(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data["content"])

    # Add more test methods here for update, destroy, and retrieve
    def test_update_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        data = {"content": "Updated comment content"}
        response = self.client.patch(
            reverse("comment-detail", args=[self.comment1.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], data["content"])

    def test_update_comment_not_authenticated(self):
        data = {"content": "Updated comment content"}
        response = self.client.patch(
            reverse("comment-detail", args=[self.comment1.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_comment(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.delete(
            reverse("comment-detail", args=[self.comment1.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Comment.objects.filter(id=self.comment1.id).exists())

    def test_destroy_comment_not_authenticated(self):
        response = self.client.delete(
            reverse("comment-detail", args=[self.comment1.id])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_comments(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.user1_token.access_token}"
        )
        response = self.client.get(reverse("comment-retrieve", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["content"], self.comment1.content)

    def test_retrieve_comments_not_authenticated(self):
        response = self.client.get(reverse("comment-retrieve", args=[self.babble1.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
