from typing import Optional, Type

from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.core.cache import caches
from django.core.cache.backends.base import BaseCache
from django.db import DatabaseError, transaction
from django.db.models import F
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import *
from ..serializers import *

user_cache: BaseCache = caches["default"]
babble_cache: BaseCache = caches["pymemcache"]


class UserViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[User] = User.objects.all()
    serializer_class: Type[UserSerializer] = UserSerializer

    def retrieve(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        if pk == None:
            user: User = request.user
        else:
            user: Optional[User] = User.objects.get_or_none(pk=pk)

        if user == None:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer: UserSerializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(
        self, request: HttpRequest, pk: Optional[int] = None
    ) -> Response:

        user: Optional[User] = User.objects.get_or_none(pk=pk)

        if user == None:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if user != request.user:
            return Response(
                {"error": "You are not allowed to do this"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer: UserSerializer = UserSerializer(
            user, data=request.data, partial=True
        )

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(
            {"message": "User updated successfully"}, status=status.HTTP_200_OK
        )

    def destroy(self, request: HttpRequest) -> Response:
        check: AbstractBaseUser | None = authenticate(
            username=request.user.username, password=request.data.get("password")
        )

        if check == None:
            return Response(
                {"error": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            with transaction.atomic():
                User.objects.filter(follower__user=check).update(
                    followers=F("followers") - 1
                )
                User.objects.filter(follower__following=check).update(
                    following=F("following") - 1
                )
                user_cache.delete(check.id)

                for babble in Babble.objects.filter(user=check):
                    babble_cache.delete(babble.id)

                check.delete()

        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["put"], url_name="password", url_path="password")
    def update_password(self, request: HttpRequest) -> Response:
        user: AbstractBaseUser | AnonymousUser = request.user

        if user.check_password(request.data.get("old_password")) == False:
            return Response(
                {"error": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user.password = make_password(request.data.get("new_password"))
        user.save()

        return Response(
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )
