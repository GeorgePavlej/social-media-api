from datetime import date, timedelta, datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import Like, User, Posts
from user.tests.test_posts_api import create_test_user, create_test_post

LIKE_URL = reverse("user:like-list")


def create_test_like(
        user: User,
        posts: Posts,
        created_at: date
) -> Like:
    return Like.objects.create(
        user=user, posts=posts, created_at=created_at
    )


class LikeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_like(self) -> None:
        user = create_test_user("test@example.com", "password")
        post = create_test_post(
            user=user,
            content="Test content",
            image="",
            created_at=date.today(),
            updated_at=date.today() + timedelta(days=2),
            hashtags="test hashtags"
        )
        self.client.force_authenticate(user)

        data = {
            "user": user.id,
            "posts": post.id,
            "created_at": date.today()
        }

        response = self.client.post(
            reverse("user:like-list"), data=data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        like = Like.objects.first()
        self.assertEqual(like.user, user)

    def test_list_like(self) -> None:
        user = create_test_user("test@example.com", "password")

        post = create_test_post(
            user=user,
            content="Test content",
            image="",
            created_at=date.today(),
            updated_at=date.today() + timedelta(days=2),
            hashtags="test hashtags"
        )

        like = create_test_like(
            user=user,
            posts=post,
            created_at=date.today()
        )

        self.client.force_authenticate(user)

        response = self.client.get(LIKE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], like.id)
        created_at_str = datetime.isoformat(
            post.created_at
        ).replace("+00:00", "Z")
        self.assertEqual(
            response.data[0]["created_at"][:19],
            created_at_str[:19]
        )
