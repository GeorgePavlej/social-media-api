import os
import uuid
from typing import Any, Optional

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _

from api_service import settings


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(
        self, email: str, password: str, **extra_fields: dict[str, Any]
    ) -> AbstractUser:
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        **extra_fields: dict[str, bool],
    ) -> AbstractUser:
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str, **extra_fields: dict[str, bool]
    ) -> AbstractUser:
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


def profile_image_file_path(instance, filename: str) -> str:
    _, extension = os.path.splitext(filename)

    filename = f"{slugify(instance.name)}--{uuid.uuid4()}{extension}"

    return os.path.join("uploads/users/", filename)


def posts_image_file_path(instance, filename: str) -> str:
    _, extension = os.path.splitext(filename)

    filename = f"{slugify(instance.user)}--{uuid.uuid4()}{extension}"

    return os.path.join("uploads/posts/", filename)


class Profile(models.Model):
    name = models.CharField(max_length=65)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to=profile_image_file_path,
        null=True,
        blank=True
    )


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="following",
        on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="followers",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self) -> str:
        return f"{self.follower} follows {self.followed}"


class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(
        upload_to=posts_image_file_path,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hashtags = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.content[:50]


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    posts = models.ForeignKey(Posts, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "posts")

    def __str__(self) -> str:
        return f"{self.user.email} likes {self.posts.content[:30]}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    posts = models.ForeignKey(Posts, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.content[:50]
