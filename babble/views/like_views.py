from typing import Optional, Type

from django.db import DatabaseError, transaction
from django.db.models import F
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class LikeViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Like] = Like.objects.all()
    serializer_class: Type[LikeSerializer] = LikeSerializer

    def create(self, request: HttpRequest) -> Response:
        serializer: LikeSerializer = LikeSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                serializer.save()

                babble: Optional[Babble] = Babble.objects.get_or_none(
                    pk=request.data.get("babble")
                )

                if babble is None:
                    raise DatabaseError

                babble.update(like_count=F("like_count") + 1)

        except DatabaseError:
            return Response({"error": "Cancle like"}, status=status.HTTP_409_CONFLICT)

        return Response(
            {"message": "Like created successfully"}, status=status.HTTP_201_CREATED
        )

    def destroy(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        like: Optional[Like] = Like.objects.get_or_none(pk=pk)

        if like is None:
            return Response(
                {"error": "Like not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                babble: Optional[Babble] = Babble.objects.get_or_none(pk=like.babble.id)

                if babble is None:
                    raise DatabaseError

                babble.update(like_count=F("like_count") - 1)
                like.delete()

        except DatabaseError:
            return Response({"error": "Cancle unlike"}, status=status.HTTP_409_CONFLICT)

        return Response(
            {"message": "Like deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        if pk is None:
            user: User = request.user
        else:
            user: Optional[User] = User.objects.get_or_none(pk=pk)

        if user is None:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        likes: BaseManager[Like] = self.queryset.filter(user=user)
        serializer: LikeBabbleSerializer = LikeBabbleSerializer(likes, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
