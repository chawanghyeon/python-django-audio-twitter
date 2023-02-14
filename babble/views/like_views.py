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
                babble.like_count += 1
                babble.save()
                serializer.save()
        except DatabaseError:
            return Response({"error": "Cancle like"}, status=status.HTTP_409_CONFLICT)

        return Response(
            {"message": "Like created successfully"}, status=status.HTTP_201_CREATED
        )

    def destroy(self, pk: Optional[int] = None) -> Response:
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
                babble.like_count -= 1
                babble.save()
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
        serializer: LikeSerializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
