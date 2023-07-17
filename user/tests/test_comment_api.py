from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User, Posts, Comment

COMMENTS_URL = reverse("user:comment-list")


class CommentsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="password"
        )
        self.post = Posts.objects.create(
            user=self.user, content="Test post", hashtags="#test"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        payload = {
            "content": "Test comment",
            "posts": self.post.id,
        }

        response = self.client.post(COMMENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(id=response.data["id"])
        self.assertEqual(comment.content, payload["content"])

    def test_create_comment(self):
        payload = {
            "content": "Test comment",
            "posts": self.post.id,
            "user": self.user.id,
        }

        response = self.client.post(COMMENTS_URL, payload)

        print(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(id=response.data["id"])
        self.assertEqual(comment.content, payload["content"])

    def test_get_comments(self):
        Comment.objects.create(
            user=self.user, posts=self.post, content="Test comment 1"
        )
        Comment.objects.create(
            user=self.user, posts=self.post, content="Test comment 2"
        )

        response = self.client.get(COMMENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
