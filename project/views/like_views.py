from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble, Like, User
from project.serializers import BabbleSerializer, LikeSerializer
from project.views.views_utils import (
    check_liked,
    check_rebabbled,
    update_babble_cache,
    update_user_cache,
)

user_cache = caches["default"]
babble_cache = caches["second"]


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        babble_pk = request.data.get("babble")

        if Like.objects.filter(babble__pk=babble_pk, user=request.user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(babble_pk=babble_pk, user=request.user)

        Babble.objects.filter(pk=babble_pk).update(like_count=F("like_count") + 1)

        update_user_cache(request.user.pk, babble_pk, "is_liked", True)
        update_babble_cache(babble_pk, "like_count", 1)

        return Response(status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        Babble.objects.filter(pk=pk).update(like_count=F("like_count") - 1)
        Like.objects.filter(babble__pk=pk, user=request.user).delete()

        pk = int(pk)

        update_user_cache(request.user.pk, pk, "is_liked", False)
        update_babble_cache(pk, "like_count", -1)

        return Response(status=status.HTTP_200_OK)

    def list(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        if pk:
            user = User.objects.get_or_404(pk=pk)
        else:
            user = request.user

        babbles = Babble.objects.filter(like__user=user).order_by("-created")
        serializer = BabbleSerializer(babbles, many=True)

        serialized_data = serializer.data
        serialized_data = check_rebabbled(serialized_data, user)
        serialized_data = check_liked(serialized_data, user)

        return Response(serialized_data, status=status.HTTP_200_OK)
