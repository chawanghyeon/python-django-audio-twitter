"""audiotwitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from babbles.views import BabbleViewSet
from comments.views import CommentViewSet
from core.views import AuthViewSet
from followers.views import FollowerViewSet
from likes.views import LikeViewSet
from notifications.views import NotificationViewSet
from rebabbles.views import RebabbleViewSet
from tags.views import TagViewSet
from users.views import UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"users/notifications", NotificationViewSet, basename="notifications")
router.register(r"users", UserViewSet, basename="users")
router.register(r"babbles", BabbleViewSet, basename="babbles")
router.register(
    r"babbles/(?P<babble_id>\d+)/comments", CommentViewSet, basename="comments"
)
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"tags", TagViewSet, basename="tags")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]

# likes
urlpatterns += [
    path(
        "babbles/<int:babble_id>/likes",
        LikeViewSet.as_view({"delete": "destroy", "post": "create"}),
        name="likes",
    ),
    path(
        "users/<int:user_id>/likes",
        LikeViewSet.as_view({"get": "list"}),
        name="likes_user",
    ),
]

# rebabbles
urlpatterns += [
    path(
        "babbles/<int:babble_id>/rebabbles",
        RebabbleViewSet.as_view({"delete": "destroy", "post": "create"}),
        name="rebabbles",
    ),
    path(
        "users/<int:user_id>/rebabbles",
        RebabbleViewSet.as_view({"get": "list"}),
        name="rebabbles_user",
    ),
]

# followers
urlpatterns += [
    path(
        "users/<int:user_id>/followers",
        FollowerViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="followers",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# swagger
urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

# Simple JWT
urlpatterns += [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
