from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from project.models import Babble, Comment
from project.serializers import CommentSerializer
from project.views.views_utils import update_babble_cache

user_cache = caches["default"]
babble_cache = caches["second"]

import logging

logger = logging.getLogger(__name__)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

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
        try:
            babble = Babble.objects.get(id=babble_id)
        except Babble.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user=request.user, babble=babble)

        babble.comment_count += 1
        babble.save()

        update_babble_cache(babble_id, "comment_count", 1)

        log_data["status"] = status.HTTP_201_CREATED
        log_data["comment_id"] = comment.id
        logger.info(log_data)

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "comment_id": pk,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        try:
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(comment, data=request.data)
        if not serializer.is_valid():
            log_data["status"] = status.HTTP_400_BAD_REQUEST
            logger.error(log_data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "comment_id": pk,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        babble_id = request.data.get("babble")
        Babble.objects.filter(id=babble_id).update(comment_count=F("comment_count") - 1)
        Comment.objects.filter(id=pk).delete()

        update_babble_cache(babble_id, "comment_count", -1)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        log_data = {
            "user": request.user.username,
            "status": "",
            "method": request.method,
            "babble_id": pk,
        }

        log_data["status"] = status.HTTP_102_PROCESSING
        logger.info(log_data)

        pagenator = CursorPagination()
        pagenator.page_size = 7
        babble = Babble.objects.get_or_404(id=pk)
        comments = Comment.objects.filter(babble=babble)
        comments = pagenator.paginate_queryset(comments, request)

        if comments is None:
            log_data["status"] = status.HTTP_404_NOT_FOUND
            logger.error(log_data)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(comments, many=True)

        log_data["status"] = status.HTTP_200_OK
        logger.info(log_data)

        return pagenator.get_paginated_response(serializer.data)
