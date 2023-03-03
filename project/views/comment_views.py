from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble, Comment
from project.serializers import CommentSerializer

user_cache = caches["default"]
babble_cache = caches["second"]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        babble_id = request.data.get("babble")
        babble = Babble.objects.get_or_404(pk=babble_id)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user=request.user, babble=babble)

        Babble.objects.filter(pk=babble_id).update(comment_count=F("comment_count") + 1)

        babble_cache_data = babble_cache.get(babble_id)
        if babble_cache_data:
            babble_cache_data["comment_count"] += 1
            babble_cache.set(babble_id, babble_cache_data, 60 * 60 * 24 * 7)

        serializer = CommentSerializer(comment)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        comment = Comment.objects.get_or_404(pk=pk)

        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save()
        serializer = CommentSerializer(comment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble_pk = request.data.get("babble")
        Babble.objects.filter(pk=babble_pk).update(comment_count=F("comment_count") - 1)
        Comment.objects.filter(pk=pk).delete()

        babble_cache_data = babble_cache.get(babble_pk)
        if babble_cache_data:
            babble_cache_data["comment_count"] -= 1
            babble_cache.set(babble_pk, babble_cache_data, 60 * 60 * 24 * 7)

        return Response(
            {"message": "Comment deleted successfully"}, status=status.HTTP_200_OK
        )

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble = Babble.objects.get_or_404(pk=pk)

        comments = Comment.objects.filter(babble=babble)
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
