from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import *
from ..serializers import *

user_cache = caches["default"]


class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_classz = FollowerSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        serializer = FollowerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        following = User.objects.get_or_404(pk=request.data.get("following"))

        request.user.update(following=F("following") + 1)
        following.update(followers=F("followers") + 1)

        user_cache.delete(request.user.id)

        return Response(
            {"message": "Follower created successfully"},
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        following = User.objects.get_or_404(pk=pk)
        follower = Follower.objects.get_or_404(User=request.user, following=following)

        request.user.update(following=F("following") - 1)
        following.update(followers=F("followers") - 1)
        follower.delete()

        user_cache.delete(request.user.id)

        return Response(
            {"message": "Follower deleted successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="followings")
    def get_followings(self, request: HttpRequest) -> Response:
        followings = self.queryset.filter(follower=request.user)
        serializer = FollowerSerializer(followings, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="followers")
    def get_followers(self, request: HttpRequest) -> Response:
        followers = self.queryset.filter(following=request.user)
        serializer = FollowerSerializer(followers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
