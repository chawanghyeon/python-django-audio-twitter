from typing import Optional

from django.contrib.auth import authenticate
from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from project.models import Babble, User
from project.serializers import UserSerializer

user_cache = caches["default"]
babble_cache = caches["second"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request: HttpRequest, id: Optional[str] = None) -> Response:
        if id:
            user = User.objects.get_or_404(id=id)
        else:
            user = request.user

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    def partial_update(self, request: HttpRequest) -> Response:
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest) -> Response:
        user = authenticate(
            username=request.user.username, password=request.data.get("password")
        )

        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        User.objects.filter(follower__user=user).update(followers=F("followers") - 1)
        User.objects.filter(follower__following=user).update(
            following=F("following") - 1
        )

        user_cache.delete(user.id)

        for babble in Babble.objects.filter(user=user):
            babble_cache.delete(babble.id)

        user.delete()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_name="password", url_path="password")
    def update_password(self, request: HttpRequest) -> Response:
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_200_OK)
