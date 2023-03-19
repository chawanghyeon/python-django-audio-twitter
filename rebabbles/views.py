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
from notifications.utils import send_message_to_user
from rebabbles.models import Rebabble
from rebabbles.serializers import RebabbleSerializer
from rebabbles.utils import (
    check_liked,
    check_rebabbled,
    get_user,
    update_babble_cache,
    update_user_cache,
)

user_cache = caches["default"]
babble_cache = caches["second"]


class RebabbleViewSet(viewsets.ModelViewSet):
    queryset = Rebabble.objects.all()
    serializer_class = RebabbleSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        babble_id = request.data.get("babble")
        babble = Babble.objects.get_or_404(id=babble_id)

        Rebabble.objects.create(user=request.user, babble=babble)

        babble.rebabble_count += 1
        babble.save()

        update_user_cache(request.user.id, babble_id, "is_rebabbled", True)
        update_babble_cache(babble_id, "rebabble_count", 1)

        send_message_to_user(
            request.user.id,
            babble.user.id,
            f"{request.user.username} rebabbled your babble {babble.id}",
        )

        return Response(status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble_id = int(pk)
        Rebabble.objects.filter(user=request.user, babble=babble_id).delete()
        Babble.objects.filter(id=babble_id).update(
            rebabble_count=F("rebabble_count") - 1
        )

        update_user_cache(request.user.id, babble_id, "is_rebabbled", False)
        update_babble_cache(babble_id, "rebabble_count", -1)

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        user = get_user(request, pk)
        pagenator = CursorPagination()
        query = Babble.objects.filter(rebabble__user=user)
        query = pagenator.paginate_queryset(query, request)

        if query is None:
            raise Http404

        serializer = BabbleSerializer(query, many=True)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return pagenator.get_paginated_response(serialized_data)
