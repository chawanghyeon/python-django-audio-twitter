from typing import Any, List, Optional, Type

from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.db import DatabaseError, transaction
from django.db.models import F, Q
from django.db.models.manager import BaseManager
from django.http import FileResponse, HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..models import *
from ..serializers import *
from ..stt import STT

stt: STT = STT()


class CommentViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Comment] = Comment.objects.all()
    serializer_class: Type[CommentSerializer] = CommentSerializer

    def create(self, request: HttpRequest) -> Response:
        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: CommentSerializer = CommentSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                serializer.save()
                serializer.data["tags"] = stt.get_keywords(serializer.data.get("audio"))
                serializer.save()

                babble: Optional[Babble] = Babble.objects.get_or_none(
                    pk=request.data.get("babble")
                )

                if babble is None:
                    raise DatabaseError

                babble.comment_count += 1
                babble.save()
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

        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: CommentSerializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        serializer.data["tags"] = stt.get_keywords(serializer.data.get("audio"))
        serializer.save()

        return Response(
            {"message": "Comment updated successfully"}, status=status.HTTP_200_OK
        )

    def destroy(self, pk: Optional[int] = None) -> Response:
        comment: Optional[Comment] = Comment.objects.get_or_none(pk=pk)
        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            with transaction.atomic():
                babble: Optional[Babble] = Babble.objects.get_or_none(
                    Babble, pk=comment.babble.id
                )
                if babble is None:
                    raise DatabaseError
                babble.comment_count -= 1
                babble.save()
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
