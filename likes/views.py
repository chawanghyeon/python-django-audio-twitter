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


class LikeViewSet(viewsets.ViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @transaction.atomic
    def create(self, request: HttpRequest, babble_id: Optional[str] = None) -> Response:
        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(babble_id=babble_id, user=request.user)

        babble = Babble.objects.get(id=babble_id)
        babble.like_count += 1
        babble.save()

        update_user_cache(request.user.id, babble_id, "is_liked", True)
        update_babble_cache(babble_id, "like_count", 1)

        send_message_to_user(
            request.user.id,
            babble.user.id,
            f"{request.user.username} liked your babble {babble.id}",
        )

        return Response(status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(
        self,
        request: HttpRequest,
        babble_id: Optional[str] = None,
    ) -> Response:
        babble_id = int(babble_id)

        Babble.objects.filter(id=babble_id).update(like_count=F("like_count") - 1)
        Like.objects.filter(user=request.user, babble=babble_id).delete()

        update_user_cache(request.user.id, babble_id, "is_liked", False)
        update_babble_cache(babble_id, "like_count", -1)

        return Response(status=status.HTTP_200_OK)

    def list(self, request: HttpRequest, user_id: Optional[str] = None) -> Response:
        user = get_user(request, user_id)
        pagenator = CursorPagination()

        query = Babble.objects.filter(like__user=user)
        query = pagenator.paginate_queryset(query, request)

        if query is None:
            raise Http404

        serializer = BabbleSerializer(query, many=True)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return pagenator.get_paginated_response(serialized_data)
