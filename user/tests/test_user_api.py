from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from user.models import User
from user.serializers import UserSerializer


class UserManagerTestCase(TestCase):
    def setUp(self) -> None:
        self.user_manager = User.objects

    def test_create_user(self) -> None:
        user = self.user_manager.create_user(
            email="test@example.com", password="test_password"
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("test_password"))

    def test_create_superuser(self) -> None:
        user = self.user_manager.create_superuser(
            email="superuser@example.com", password="super_password"
        )

        self.assertEqual(user.email, "superuser@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("super_password"))

    def test_create_user_missing_email(self) -> None:
        with self.assertRaises(ValueError):
            self.user_manager.create_user(email=None, password="test_password")

    def test_create_superuser_wrong_permissions(self) -> None:
        with self.assertRaises(ValueError):
            self.user_manager.create_superuser(
                email="superuser@example.com",
                password="super_password",
                is_staff=False,
            )

        with self.assertRaises(ValueError):
            self.user_manager.create_superuser(
                email="superuser@example.com",
                password="super_password",
                is_superuser=False,
            )


class UserModelTestCase(TestCase):
    def test_create_user_instance(self) -> None:
        user = User.objects.create_user(
            email="test@example.com", password="test_password"
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("test_password"))

    def test_create_user_with_same_email(self) -> None:
        User.objects.create_user(
            email="duplicate@example.com", password="test_password"
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="duplicate@example.com", password="another_password"
            )


class UserSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_user_serialization(self) -> None:
        user = User.objects.create_user(
            email="test@example.com", password="test_password",
        )
        serializer = UserSerializer(user)

        expected_data = {
            "id": user.id,
            "email": "test@example.com",
            "is_staff": False,
            "following": [],
            "followers": []
        }

        self.assertEqual(serializer.data, expected_data)

    def test_create_user(self) -> None:
        user_data = {
            "email": "create@example.com",
            "password": "test_password"
        }

        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = User.objects.get(email="create@example.com")
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("test_password"))

    def test_update_user(self) -> None:
        user = User.objects.create_user(
            email="update@example.com",
            password="old_password"
        )
        update_data = {
            "email": "update@example.com",
            "password": "new_password"
        }

        serializer = UserSerializer(
            instance=user, data=update_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.refresh_from_db()
        self.assertTrue(user.check_password("new_password"))
