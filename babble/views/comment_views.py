from typing import List, Optional, Type

from django.db import DatabaseError, transaction
from django.db.models import F
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..stt import STT

stt: STT = STT()


class CommentViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Comment] = Comment.objects.all()
    serializer_class: Type[CommentSerializer] = CommentSerializer

    def save_keywords(self, comment: Comment) -> Comment:
        keywords: List[str] = stt.get_keywords(comment.audio.path)

        for keyword in keywords:
            tag: Tag = Tag.objects.get_or_create(text=keyword)
            comment.tags.add(tag)

        comment.save()

        return comment

    def create(self, request: HttpRequest) -> Response:
        serializer: CommentSerializer = CommentSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                comment: Comment = serializer.save()
                comment = self.save_keywords(comment)

                babble: Optional[Babble] = Babble.objects.get_or_none(
                    pk=request.data.get("babble")
                )

                if babble is None:
                    raise DatabaseError

                babble.update(comment_count=F("comment_count") + 1)

        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Comment created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        comment: Comment = Comment.objects.get_or_none(pk=pk)

        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer: CommentSerializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comment: Comment = serializer.save()
        comment = self.save_keywords(comment)

        serializer: CommentSerializer = CommentSerializer(comment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        comment: Optional[Comment] = Comment.objects.get_or_none(pk=pk)

        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                babble: Optional[Babble] = Babble.objects.get_or_none(
                    pk=comment.babble.id
                )

                if babble is None:
                    raise DatabaseError

                babble.update(comment_count=F("comment_count") - 1)
                comment.delete()

        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Comment deleted successfully"}, status=status.HTTP_200_OK
        )

    def retrieve(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        babble: Optional[Babble] = Babble.objects.get_or_none(pk=pk)

        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )

        comments: BaseManager[Comment] = self.queryset.filter(babble=babble)
        serializer: CommentSerializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
