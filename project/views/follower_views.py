import logging
from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Follower, User
from project.serializers import FollowerSerializer

logger = logging.getLogger(__name__)

user_cache = caches["default"]


class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "following": request.data.get("following"),
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        try:
            following = User.objects.get(id=request.data.get("following"))
        except User.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = FollowerSerializer(data=request.data)
        if not serializer.is_valid():
            log_data["status"] = status.HTTP_400_BAD_REQUEST
            logger.error(log_data)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user, following=following)

        User.objects.filter(id=request.user.id).update(
            following_count=F("following_count") + 1
        )
        User.objects.filter(id=following.id).update(
            follower_count=F("follower_count") + 1
        )

        user_cache.delete(request.user.id)

        log_data["status"] = status.HTTP_201_CREATED
        logger.info(log_data)

        return Response(
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "babble_id": request.data.get("babble"),
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        try:
            Follower.objects.filter(user=request.user, following=pk).delete()
        except Follower.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        User.objects.filter(id=pk).update(follower_count=F("follower_count") - 1)
        User.objects.filter(id=request.user.id).update(
            following_count=F("following_count") - 1
        )

        user_cache.delete(request.user.id)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(status=status.HTTP_200_OK)
