from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import Http404, HttpRequest
from rest_framework import status, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from babbles.models import Babble
from comments.models import Comment
from comments.serializers import CommentSerializer
from comments.utils import update_babble_cache
from notifications.utils import send_message_to_user

user_cache = caches["default"]
babble_cache = caches["second"]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @transaction.atomic
    def create(self, request: HttpRequest, babble_id: Optional[str] = None) -> Response:
        babble = Babble.objects.get_or_404(id=babble_id)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user=request.user, babble=babble)

        babble.comment_count += 1
        babble.save()

        send_message_to_user(
            request.user.id,
            babble.user.id,
            f"{request.user.username} commented on your babble {babble.id}.",
        )

        update_babble_cache(babble_id, "comment_count", 1)
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(
        self,
        request: HttpRequest,
        babble_id: Optional[str] = None,
        pk: Optional[str] = None,
    ) -> Response:
        comment = Comment.objects.get_or_404(id=pk)

        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save()

        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(
        self,
        request: HttpRequest,
        babble_id: Optional[str] = None,
        pk: Optional[str] = None,
    ) -> Response:
        Babble.objects.filter(id=babble_id).update(comment_count=F("comment_count") - 1)
        Comment.objects.filter(id=pk).delete()

        update_babble_cache(babble_id, "comment_count", -1)

        return Response(status=status.HTTP_200_OK)

    def list(self, request: HttpRequest, babble_id: Optional[str] = None) -> Response:
        pagenator = CursorPagination()
        pagenator.page_size = 7
        babble = Babble.objects.get_or_404(id=babble_id)
        query = Comment.objects.filter(babble=babble)
        query = pagenator.paginate_queryset(query, request)

        if query is None:
            raise Http404

        serializer = CommentSerializer(query, many=True)

        return pagenator.get_paginated_response(serializer.data)
