from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Profile, User, Follow, Posts, Like, Comment
from user.permissions import IsOwnerOrReadOnly
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    ProfileSerializer,
    FollowSerializer,
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> User:
        return self.request.user

    def post(self, request, *args: Any, **kwargs: Any) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        response = Response({"message": "Logged out successfully"})
        response.delete_cookie("refresh_token")

        return response


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class ProfileUserViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                description="Filter by name (ex. ?name=George)",
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="bio",
                type=str,
                description="Filter by bio (ex. ?bio=info from bio field)",
                location=OpenApiParameter.QUERY
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FollowUserViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer: Serializer) -> None:
        followed_user = User.objects.get(
            id=serializer.validated_data["followed"].id
        )

        if self.request.user == followed_user:
            raise ValidationError({"message": "You cannot follow yourself."})

        if Follow.objects.filter(
            follower=self.request.user, followed=followed_user
        ).exists():
            raise ValidationError(
                {
                    "message": "You are already following this user."
                }
            )

        serializer.save(follower=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Posts.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="content",
                type=str,
                description="Filter by content (ex. ?content=)",
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="hashtags",
                type=str,
                description="Filter by hashtags (ex. ?hashtags=Summer)",
                location=OpenApiParameter.QUERY
            ),
        ]
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)

    def get_queryset(self) -> QuerySet[Posts]:
        user = self.request.user
        content = self.request.query_params.get("content", None)
        hashtags = self.request.query_params.get("hashtags", None)
        queryset = Posts.objects.all()

        if content:
            queryset = queryset.filter(content__icontains=content)

        if hashtags:
            queryset = queryset.filter(hashtags__icontains=hashtags)

        return queryset.filter(user=user) | queryset.filter(
            user__in=user.following.values_list("followed", flat=True)
        )


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated)

    def perform_create(self, serializer: Serializer) -> None:
        user = self.request.user
        post = serializer.validated_data["posts"]
        if Like.objects.filter(user=user, posts=post).exists():
            raise ValidationError("You have already liked this post.")
        serializer.save(user=user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)
