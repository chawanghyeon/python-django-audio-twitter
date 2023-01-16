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
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from babble import views

router = DefaultRouter()
router.register(r"user", views.UserViewSet, basename="user")
router.register(r"babble", views.BabbleViewSet, basename="babble")
router.register(r"comment", views.CommentViewSet, basename="comment")
router.register(r"follower", views.FollowerViewSet, basename="follower")
router.register(r"like", views.LikeViewSet, basename="like")
router.register(r"auth", views.AuthViewSet, basename="auth")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]

# docs setting
urlpatterns += [
    # YOUR PATTERNS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/schema/json/", SpectacularJSONAPIView.as_view(), name="schema-json"),
]
