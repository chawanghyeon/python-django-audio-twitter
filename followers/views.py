from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from followers.models import Follower
from followers.serializers import FollowerSerializer
from notifications.utils import send_message_to_user
from users.models import User

user_cache = caches["default"]


class FollowerViewSet(viewsets.ViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer

    @transaction.atomic
    def create(self, request: HttpRequest, user_id: Optional[str] = None) -> Response:
        serializer = FollowerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, following_id=user_id)

        User.objects.filter(id=request.user.id).update(
            following_count=F("following_count") + 1
        )
        User.objects.filter(id=user_id).update(follower_count=F("follower_count") + 1)
        user_cache.delete(request.user.id)

        send_message_to_user(
            request.user.id, user_id, f"{request.user.username} followed you"
        )

        return Response(status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request: HttpRequest, user_id: Optional[str] = None) -> Response:
        Follower.objects.filter(user=request.user, following=user_id).delete()

        User.objects.filter(id=user_id).update(follower_count=F("follower_count") - 1)
        User.objects.filter(id=request.user.id).update(
            following_count=F("following_count") - 1
        )
        user_cache.delete(request.user.id)

        return Response(status=status.HTTP_200_OK)
