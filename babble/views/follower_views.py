from typing import Dict, List, Optional, Type

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


class FollowerViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Follower] = Follower.objects.all()
    serializer_classz: Type[FollowerSerializer] = FollowerSerializer

    def create(self, request: HttpRequest) -> Response:
        serializer: FollowerSerializer = FollowerSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                serializer.save()

                user: Optional[User] = User.objects.get_or_none(
                    pk=request.data.get("user")
                )
                following: Optional[User] = User.objects.get_or_none(
                    pk=request.data.get("following")
                )

                if user is None or following is None:
                    raise DatabaseError

                user.update(following=F("following") + 1)
                following.update(followers=F("followers") + 1)

                user_cache.delete(user.id)

        except DatabaseError:
            return Response(
                {"error": "Cancle follower"}, status=status.HTTP_409_CONFLICT
            )

        return Response(
            {"message": "Follower created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        following: Optional[User] = User.objects.get_or_none(pk=pk)
        follower: Optional[Follower] = Follower.objects.get_or_none(
            User=request.user, following=following
        )

        if following is None or follower is None:
            return Response({"error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                request.user.update(following=F("following") - 1)
                following.update(followers=F("followers") - 1)
                follower.delete()

                user_cache.delete(request.user.id)

        except DatabaseError:
            return Response(
                {"error": "Cancle follower"}, status=status.HTTP_409_CONFLICT
            )

        return Response(
            {"message": "Follower deleted successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="followings")
    def get_followings(self, request: HttpRequest) -> Response:
        follower: List[Follower] = self.queryset.filter(follower=request.user)
        serializer: FollowerSerializer = FollowerSerializer(follower, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="followers")
    def get_followers(self, request: HttpRequest) -> Response:
        follower: List[Follower] = self.queryset.filter(following=request.user)
        serializer: FollowerSerializer = FollowerSerializer(follower, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
