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
        logger.info(
            f"Received POST request to create a new babble by user {request.user.username}"
        )

        serializer = BabbleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            babble = serializer.save(user=request.user)
            logger.info(
                f"New babble created with id {babble.id} by user {request.user.username}"
            )

            babble = save_keywords(babble)
            serializer = BabbleSerializer(babble)
            logger.info(
                f"Keywords are {serializer.data.get('tags')} for babble with id {babble.id} by user {request.user.username}"
            )
            set_caches(babble, request.user, serializer.data)

            response = Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            logger.warning(
                f"Validation errors occurred while creating a new babble by user {request.user.username}: {serializer.errors}"
            )

        return response

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        pk = int(pk)
        babble_data = babble_cache.get(pk)

        if babble_data is None:
            babble = Babble.objects.get(id=pk)
            babble_data = BabbleSerializer(babble).data
            babble_cache.set(pk, babble_data)

        is_rebabbled = Rebabble.objects.filter(user=request.user, babble=pk).exists()
        is_liked = Like.objects.filter(user=request.user, babble=pk).exists()

        babble_data["is_rebabbled"] = is_rebabbled
        babble_data["is_liked"] = is_liked

        return Response(babble_data, status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble = Babble.objects.get_or_404(id=pk)
        serializer = BabbleSerializer(babble, data=request.data)
        serializer.is_valid(raise_exception=True)

        babble = serializer.save()
        babble = save_keywords(babble)

        set_follower_cache(babble, request.user)

        return Response(BabbleSerializer(babble).data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        pk = int(pk)
        Babble.objects.filter(id=pk).delete()
        babble_cache.delete(pk)

        return Response(status=status.HTTP_200_OK)

    def list(self, request: HttpRequest) -> Response:
        user = get_user(request)
        user_cache_data = user_cache.get(user.id)
        next = request.query_params.get("next") or 0
        next = int(next)

        if user_cache_data:
            serialized_data = get_babbles_from_cache(user_cache_data, user, next)
        else:
            serialized_data = get_babbles_from_db(user, next)

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
        pagenator = CursorPagination()
        babbles = Babble.objects.exclude(user=request.user)
        babbles = pagenator.paginate_queryset(babbles, request)

        if babbles is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BabbleSerializer(babbles, many=True)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return pagenator.get_paginated_response(serialized_data)

    @action(detail=True, methods=["get"])
    def profile(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        user = get_user(request, pk)
        pagenator = CursorPagination()

        babbles = Babble.objects.filter(user=user)
        babbles = pagenator.paginate_queryset(babbles, request)

        if babbles is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BabbleSerializer(babbles, many=True)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return pagenator.get_paginated_response(serialized_data)
