import logging
from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import Http404, HttpRequest
from rest_framework import status, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from babbles.models import Babble
from babbles.serializers import BabbleSerializer
from likes.models import Like
from likes.serializers import LikeSerializer
from likes.utils import (
    check_liked,
    check_rebabbled,
    get_user,
    update_babble_cache,
    update_user_cache,
)
from notifications.utils import send_message_to_user

logger = logging.getLogger(__name__)

user_cache = caches["default"]
babble_cache = caches["second"]


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        babble_id = request.data.get("babble")
        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        babble = Babble.objects.get_or_404(id=babble_id)
        serializer.save(babble=babble, user=request.user)

        babble.like_count += 1
        babble.save()

        update_user_cache(request.user.id, babble_id, "is_liked", True)
        update_babble_cache(babble_id, "like_count", 1)

        send_message_to_user(
            request.user,
            babble.user,
            f"{request.user.username} liked your babble {babble.id}",
        )

        return Response(status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        pk = int(pk)

        Babble.objects.filter(id=pk).update(like_count=F("like_count") - 1)
        Like.objects.filter(babble__id=pk, user=request.user).delete()

        update_user_cache(request.user.id, pk, "is_liked", False)
        update_babble_cache(pk, "like_count", -1)

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        user = get_user(request, pk)
        pagenator = CursorPagination()

        query = Babble.objects.filter(like__user=user)
        query = pagenator.paginate_queryset(query, request)

        if query is None:
            raise Http404

        serializer = BabbleSerializer(query, many=True)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return pagenator.get_paginated_response(serialized_data)
