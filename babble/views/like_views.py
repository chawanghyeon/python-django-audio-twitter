from typing import Optional

from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        babble_id = request.data.get("babble")

        if Like.objects.filter(babble__pk=babble_id, user=request.user).exists():
            return Response(
                {"message": "Like already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(babble_id=babble_id, user=request.user)

        Babble.objects.filter(pk=babble_id).update(like_count=F("like_count") + 1)

        return Response(
            {"message": "Like created successfully"}, status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        like = Like.objects.get_or_404(babble__pk=pk, user=request.user)

        like.babble.update(like_count=F("like_count") - 1)
        like.delete()

        return Response(
            {"message": "Like deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        if pk:
            user = User.objects.get_or_404(pk=pk)
        else:
            user = request.user

        likes = self.queryset.filter(user=user)
        serializer = LikeBabbleSerializer(likes, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
