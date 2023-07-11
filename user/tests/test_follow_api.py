from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User, Follow
from user.tests.test_posts_api import create_test_user

FOLLOW_URL = reverse("user:follow-list")


def create_test_follow(
        follower: User,
        followed: User
) -> Follow:
    return Follow.objects.create(
        follower=follower, followed=followed
    )


class FollowApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_follow(self) -> None:
        follower = create_test_user("test1@example.com", "password")
        followed = create_test_user("test2@example.com", "password")
        self.client.force_authenticate(follower)

        data = {
            "follower": follower.id,
            "followed": followed.id,
        }

        response = self.client.post(
            FOLLOW_URL, data=data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 1)
        follow = Follow.objects.first()
        self.assertEqual(follow.follower, follower)
        self.assertEqual(follow.followed, followed)

    def test_delete_follow(self) -> None:
        follower = create_test_user("test1@example.com", "password")
        followed = create_test_user("test2@example.com", "password")
        follow = create_test_follow(follower=follower, followed=followed)

        self.client.force_authenticate(follower)

        response = self.client.delete(
            reverse("user:follow-detail", kwargs={"pk": follow.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Follow.objects.count(), 0)
