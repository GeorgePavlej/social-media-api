from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, filters
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Profile, User, Follow, Posts, Like, Comment
from user.permissions import IsOwnerOrReadOnly
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    ProfileSerializer,
    FollowSerializer,
    PostSerializer, LikeSerializer, CommentSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        response = Response({"message": "Logged out successfully"})
        response.delete_cookie("refresh_token")

        return response


class ProfileUserViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["bio", "name"]
    permission_classes = (IsOwnerOrReadOnly,)


class FollowUserViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer) -> None:
        followed_user = User.objects.get(id=serializer.validated_data["followed"].id)

        if self.request.user == followed_user:
            raise ValidationError({"message": "You cannot follow yourself."})

        if Follow.objects.filter(
            follower=self.request.user, followed=followed_user
        ).exists():
            raise ValidationError({"message": "You are already following this user."})

        serializer.save(follower=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Posts.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["content", "hashtags"]

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Posts.objects.filter(user=user) | Posts.objects.filter(
            user__in=user.following.values_list("followed", flat=True)
        )


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)
