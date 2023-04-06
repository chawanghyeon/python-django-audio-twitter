from typing import Optional

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from babbles.models import Babble
from users.models import User
from users.serializers import UserSerializer
from users.utils import check_is_following, get_user

user_cache = caches["default"]
babble_cache = caches["second"]


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        user = get_user(request, pk)
        serializer = UserSerializer(user)
        serialized_data = check_is_following(request.user, user, serializer.data)

        return Response(serialized_data, status=status.HTTP_200_OK)

    def partial_update(
        self, request: HttpRequest, pk: Optional[str] = None
    ) -> Response:
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        user = authenticate(
            username=request.user.username, password=request.data.get("password")
        )

        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        User.objects.filter(self__following=user).update(
            follower_count=F("follower_count") - 1
        )
        User.objects.filter(following__user=user).update(
            following_count=F("following_count") - 1
        )

        user_cache.delete(user.id)

        for babble in Babble.objects.filter(user=user):
            babble_cache.delete(babble.id)

        user.delete()

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_name="password", url_path="password")
    def update_password(self, request: HttpRequest) -> Response:
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user.password = make_password(new_password)
        user.save()

        return Response(status=status.HTTP_200_OK)
