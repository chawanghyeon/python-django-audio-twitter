from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble, Comment
from project.serializers import CommentSerializer
from project.views.views_utils import update_babble_cache

user_cache = caches["default"]
babble_cache = caches["second"]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        babble_id = request.data.get("babble")
        babble = Babble.objects.get_or_404(id=babble_id)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user=request.user, babble=babble)

        babble.comment_count += 1
        babble.save()

        update_babble_cache(babble_id, "comment_count", 1)

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: HttpRequest, id: Optional[str] = None) -> Response:
        comment = Comment.objects.get_or_404(id=id)

        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save()

        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest, id: Optional[str] = None) -> Response:
        babble_id = request.data.get("babble")
        Babble.objects.filter(id=babble_id).update(comment_count=F("comment_count") - 1)
        Comment.objects.filter(id=id).delete()

        update_babble_cache(babble_id, "comment_count", -1)

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request: HttpRequest, id: Optional[str] = None) -> Response:
        babble = Babble.objects.get_or_404(id=id)
        comments = Comment.objects.filter(babble=babble)

        return Response(
            CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK
        )
