from datetime import date, timedelta, datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User, Like, Posts

POST_URL = reverse("user:posts-list")


def create_test_user(email: str, password: str) -> User:
    return User.objects.create_user(email=email, password=password)


def create_test_like(
        user: User,
        posts: Posts,
        created_at: date
) -> Like:
    return Like.objects.create(
        user=user, posts=posts, created_at=created_at
    )


def create_test_post(
        user: User,
        content: str,
        image: str,
        created_at: date,
        updated_at: date,
        hashtags: str
) -> Posts:
    return Posts.objects.create(
        user=user,
        content=content,
        image=image,
        created_at=created_at,
        updated_at=updated_at,
        hashtags=hashtags
    )


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_post(self) -> None:
        user = create_test_user("test@example.com", "password")

        self.client.force_authenticate(user)

        data = {
            "user": user.id,
            "content": "Test content",
            "image": "",
            "created_at": date.today(),
            "updated_at": date.today() + timedelta(days=2),
            "hashtags": "Test hashtags"
        }

        response = self.client.post(
            reverse("user:posts-list"), data=data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Posts.objects.count(), 1)
        post = Posts.objects.first()
        self.assertEqual(post.user, user)

    def test_list_post(self) -> None:
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

        response = self.client.get(POST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], post.id)
        self.assertEqual(response.data[0]["content"], post.content)
        self.assertEqual(response.data[0]["image"], None)
        created_at_str = datetime.isoformat(
            post.created_at
        ).replace("+00:00", "Z")
        self.assertEqual(response.data[0]["created_at"], created_at_str)
        updated_at_str = datetime.isoformat(
            post.updated_at
        ).replace("+00:00", "Z")
        self.assertEqual(response.data[0]["updated_at"], updated_at_str)
        self.assertEqual(response.data[0]["hashtags"], post.hashtags)
