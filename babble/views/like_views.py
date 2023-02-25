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
        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        babble = Babble.objects.get_or_404(id=request.data.get("babble"))
        babble.update(like_count=F("like_count") + 1)

        return Response(
            {"message": "Like created successfully"}, status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, id: Optional[int] = None) -> Response:
        like = Like.objects.select_related("babble").get_or_404(id=id)

        like.babble.update(like_count=F("like_count") - 1)
        like.delete()

        return Response(
            {"message": "Like deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest, id: Optional[int] = None) -> Response:
        if id:
            user = User.objects.get_or_404(id=id)
        else:
            user = request.user

        likes = self.queryset.filter(user=user)
        serializer = LikeBabbleSerializer(likes, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
