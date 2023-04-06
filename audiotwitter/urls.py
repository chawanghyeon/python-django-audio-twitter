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

router = DefaultRouter()
router.register(r"user", UserViewSet, basename="user")
router.register(r"babble", BabbleViewSet, basename="babble")
router.register(
    r"babble/(?P<babble_id>\d+)/comment", CommentViewSet, basename="comment"
)
router.register(r"follower", FollowerViewSet, basename="follower")
router.register(r"like", LikeViewSet, basename="like")
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"tag", TagViewSet, basename="tag")
router.register(r"rebabble", RebabbleViewSet, basename="rebabble")
router.register(r"notification", NotificationViewSet, basename="notification")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
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
