import logging
from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from project.models import Babble, Like
from project.serializers import BabbleSerializer, LikeSerializer
from project.views.views_utils import (
    check_liked,
    check_rebabbled,
    get_user,
    update_babble_cache,
    update_user_cache,
)

logger = logging.getLogger(__name__)

user_cache = caches["default"]
babble_cache = caches["second"]


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "babble_id": request.data.get("babble"),
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        babble_id = request.data.get("babble")
        serializer = LikeSerializer(data=request.data)

        if (
            Like.objects.filter(babble__id=babble_id, user=request.user).exists()
            and not serializer.is_valid()
        ):
            log_data["status"] = status.HTTP_400_BAD_REQUEST
            logger.error(log_data)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save(babble_id=babble_id, user=request.user)

        Babble.objects.filter(id=babble_id).update(like_count=F("like_count") + 1)

        update_user_cache(request.user.id, babble_id, "is_liked", True)
        update_babble_cache(babble_id, "like_count", 1)

        log_data["status"] = status.HTTP_201_CREATED
        logger.info(log_data)

        return Response(status=status.HTTP_201_CREATED)

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
            Babble.objects.filter(id=pk).update(like_count=F("like_count") - 1)
        except Babble.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            Like.objects.filter(babble__id=pk, user=request.user).delete()
        except Like.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        pk = int(pk)

        update_user_cache(request.user.id, pk, "is_liked", False)
        update_babble_cache(pk, "like_count", -1)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "user_id": pk,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        user = get_user(request, pk)
        pagenator = CursorPagination()

        babbles = Babble.objects.filter(like__user=user)
        babbles = pagenator.paginate_queryset(babbles, request)

        if babbles is None:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BabbleSerializer(babbles, many=True)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return pagenator.get_paginated_response(serialized_data)
