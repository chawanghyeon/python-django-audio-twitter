import logging
from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from project.models import Babble, Rebabble
from project.serializers import BabbleSerializer, RebabbleSerializer
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


class RebabbleViewSet(viewsets.ModelViewSet):
    queryset = Rebabble.objects.all()
    serializer_class = RebabbleSerializer

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

        id = request.data.get("babble")

        if Rebabble.objects.filter(user=request.user, babble=id).exists():
            log_data["status"] = status.HTTP_400_BAD_REQUEST
            logger.error(log_data)
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            babble = Babble.objects.get(id=id)
        except Babble.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )
        babble.rebabble_count += 1
        babble.save()

        Rebabble.objects.create(user=request.user, babble=babble)

        update_user_cache(request.user.id, id, "is_rebabbled", True)
        update_babble_cache(id, "rebabble_count", 1)

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

        pk = int(pk)

        try:
            Rebabble.objects.filter(user=request.user, babble=pk).delete()
        except Rebabble.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            Babble.objects.filter(id=pk).update(rebabble_count=F("rebabble_count") - 1)
        except Babble.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        update_user_cache(request.user.id, pk, "is_rebabbled", False)
        update_babble_cache(pk, "rebabble_count", -1)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(
            status=status.HTTP_200_OK,
        )

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
        babbles = Babble.objects.filter(rebabble__user=user)
        babbles = pagenator.paginate_queryset(babbles, request)

        if babbles is None:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BabbleSerializer(babbles, many=True)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return pagenator.get_paginated_response(serialized_data)
