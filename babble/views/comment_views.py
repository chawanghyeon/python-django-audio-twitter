from typing import Optional

from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..stt import STT

stt = STT()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        babble_id = request.data.get("babble")
        babble = Babble.objects.get_or_404(pk=babble_id)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        babble.update(comment_count=F("comment_count") + 1)

        return Response(
            {"message": "Comment created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        comment = Comment.objects.get_or_404(pk=pk)

        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save()
        serializer = CommentSerializer(comment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        comment = Comment.objects.get_or_404(pk=pk)
        babble = Babble.objects.get_or_404(pk=comment.babble.id)

        babble.update(comment_count=F("comment_count") - 1)
        comment.delete()

        return Response(
            {"message": "Comment deleted successfully"}, status=status.HTTP_200_OK
        )

    def retrieve(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        babble = Babble.objects.get_or_404(pk=pk)

        comments = Comment.objects.filter(babble=babble)
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
