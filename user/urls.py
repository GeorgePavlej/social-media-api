from django.urls import path
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from user.views import (
    CreateUserView,
    ManageUserView,
    ProfileUserViewSet,
    FollowUserViewSet,
)

router = DefaultRouter()
router.register("profile", ProfileUserViewSet)
router.register("follow", FollowUserViewSet, basename="follow")

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ManageUserView.as_view(), name="manage"),
] + router.urls

app_name = "user"
