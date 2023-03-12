import logging
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
from project.views.views_utils import check_is_following, get_user

logger = logging.getLogger(__name__)
user_cache = caches["default"]
babble_cache = caches["second"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "user_id": pk,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        try:
            user = get_user(request, pk)
        except User.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        serialized_data = check_is_following(request.user, user, serializer.data)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(serialized_data, status=status.HTTP_200_OK)

    def partial_update(self, request: HttpRequest) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "babble_id": request.data.get("babble"),
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            log_data["status"] = status.HTTP_400_BAD_REQUEST
            logger.error(log_data)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "babble_id": request.data.get("babble"),
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        user = authenticate(
            username=request.user.username, password=request.data.get("password")
        )

        if user is None:
            log_data["status"] = status.HTTP_401_UNAUTHORIZED
            logger.error(log_data)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        User.objects.filter(follower__user=user).update(
            follower_count=F("follower_count") - 1
        )
        User.objects.filter(follower__following=user).update(
            following_count=F("following_count") - 1
        )

        user_cache.delete(user.id)

        for babble in Babble.objects.filter(user=user):
            babble_cache.delete(babble.id)

        user.delete()

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_name="password", url_path="password")
    def update_password(self, request: HttpRequest) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "babble_id": request.data.get("babble"),
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            log_data["status"] = status.HTTP_401_UNAUTHORIZED
            logger.error(log_data)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user.set_password(new_password)
        user.save()

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(status=status.HTTP_200_OK)
