import logging
from typing import Optional, Type

from django.core.cache import caches
from django.db import transaction
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from project.models import Babble, Like, Rebabble
from project.serializers import BabbleSerializer
from project.views.views_utils import (
    check_liked,
    check_rebabbled,
    get_babbles_from_cache,
    get_babbles_from_db,
    get_user,
    save_keywords,
    set_caches,
    set_follower_cache,
)

logger = logging.getLogger(__name__)

user_cache = caches["default"]
babble_cache = caches["second"]

user_cache.clear()
babble_cache.clear()


class BabbleViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        log_data = {
            "user": request.user.username,
            "model": "Babble",
            "action": "create",
            "status": "",
            "method": request.method,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        serializer = BabbleSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            log_data["status"] = status.HTTP_400_BAD_REQUEST
            logger.error(log_data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        babble = serializer.save(user=request.user)
        babble = save_keywords(babble)
        serializer = BabbleSerializer(babble)
        set_caches(babble, request.user, serializer.data)

        log_data["status"] = status.HTTP_201_CREATED
        log_data["babble_id"] = babble.id
        log_data["keywords"] = serializer.data["keywords"]
        logger.info(log_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "model": "Babble",
            "action": "retrieve",
            "status": "",
            "babble_id": pk,
            "method": request.method,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        pk = int(pk)
        babble_data = babble_cache.get(pk)

        if babble_data is None:
            try:
                babble = Babble.objects.get(id=pk)
            except Babble.DoesNotExist:
                log_data["status"] = status.HTTP_404_NOT_FOUND
                logger.error(log_data)
                return Response(status=status.HTTP_404_NOT_FOUND)

            babble_data = BabbleSerializer(babble).data
            babble_cache.set(pk, babble_data)

        is_rebabbled = Rebabble.objects.filter(user=request.user, babble=pk).exists()
        is_liked = Like.objects.filter(user=request.user, babble=pk).exists()

        babble_data["is_rebabbled"] = is_rebabbled
        babble_data["is_liked"] = is_liked

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(babble_data, status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "model": "Babble",
            "action": "update",
            "status": "",
            "babble_id": pk,
            "method": request.method,
        }
        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        try:
            babble = Babble.objects.get(id=pk)
        except Babble.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BabbleSerializer(babble, data=request.data)
        serializer.is_valid(raise_exception=True)

        babble = serializer.save()
        babble = save_keywords(babble)
        set_follower_cache(babble, request.user)

        serializer = BabbleSerializer(babble)
        log_data["status"] = status.HTTP_200_OK
        log_data["keywords"] = serializer.data["keywords"]
        logger.info(log_data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "model": "Babble",
            "action": "destroy",
            "status": "",
            "babble_id": pk,
            "method": request.method,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)
        pk = int(pk)

        try:
            Babble.objects.filter(id=pk).delete()
        except Exception:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(status=status.HTTP_200_OK)

    def list(self, request: HttpRequest) -> Response:
        log_data = {
            "user": request.user.username,
            "model": "Babble",
            "action": "list",
            "status": "",
            "method": request.method,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        user = get_user(request)
        user_cache_data = user_cache.get(user.id)
        next = request.query_params.get("next") or 0
        next = int(next)

        if user_cache_data:
            serialized_data = get_babbles_from_cache(user_cache_data, user, next)
            log_data["status"] = status.HTTP_200_OK
            log_data["from"] = "cache"
            logger.info(log_data)
        else:
            serialized_data = get_babbles_from_db(user, next)
            log_data["status"] = status.HTTP_200_OK
            log_data["from"] = "db"
            logger.info(log_data)

        if user != request.user:
            serialized_data = check_rebabbled(serialized_data, request.user)
            serialized_data = check_liked(serialized_data, request.user)

        return Response(
            {
                "results": serialized_data,
                "next": next + 5,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def explore(self, request: HttpRequest) -> Response:
        log_data = {
            "user": request.user.username,
            "model": "Babble",
            "action": "explore",
            "status": "",
            "method": request.method,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        pagenator = CursorPagination()
        babbles = Babble.objects.exclude(user=request.user)
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

    @action(detail=True, methods=["get"])
    def profile(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "model": "Babble",
            "action": "profile",
            "status": "",
            "babble_id": pk,
            "method": request.method,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        user = get_user(request, pk)
        pagenator = CursorPagination()

        babbles = Babble.objects.filter(user=user)
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
