from django.test import TestCase

from user.models import User, Profile
from user.tests.test_posts_api import create_test_user


def create_test_profile(user: User, name: str, bio: str) -> Profile:
    return Profile.objects.create(user=user, name=name, bio=bio)


class ProfileModelTests(TestCase):
    def test_create_profile(self):
        user = create_test_user("test@example.com", "password")
        profile = create_test_profile(user, "Test User", "This is a test bio")

        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.name, "Test User")
        self.assertEqual(profile.bio, "This is a test bio")

    def test_str_representation(self):
        user = create_test_user("test@example.com", "password")
        profile = create_test_profile(user, "Test User", "This is a test bio")

        self.assertEqual(str(profile.name), "Test User")

    def test_user_deletion_cascades(self):
        user = create_test_user("test@example.com", "password")
        create_test_profile(user, "Test User", "This is a test bio")

        user.delete()

        self.assertEqual(Profile.objects.count(), 0)
