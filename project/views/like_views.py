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
        babble_id = request.data.get("babble")

        if Like.objects.filter(babble__id=babble_id, user=request.user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(babble_id=babble_id, user=request.user)

        Babble.objects.filter(id=babble_id).update(like_count=F("like_count") + 1)

        update_user_cache(request.user.id, babble_id, "is_liked", True)
        update_babble_cache(babble_id, "like_count", 1)

        return Response(status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request: HttpRequest, id: Optional[str] = None) -> Response:
        Babble.objects.filter(id=id).update(like_count=F("like_count") - 1)
        Like.objects.filter(babble__id=id, user=request.user).delete()

        id = int(id)

        update_user_cache(request.user.id, id, "is_liked", False)
        update_babble_cache(id, "like_count", -1)

        return Response(status=status.HTTP_200_OK)

    def list(self, request: HttpRequest, id: Optional[str] = None) -> Response:
        if id:
            user = User.objects.get_or_404(id=id)
        else:
            user = request.user

        babbles = Babble.objects.filter(like__user=user).order_by("-created")
        serializer = BabbleSerializer(babbles, many=True)

        serialized_data = serializer.data
        serialized_data = check_rebabbled(serialized_data, user)
        serialized_data = check_liked(serialized_data, user)

        return Response(serialized_data, status=status.HTTP_200_OK)
