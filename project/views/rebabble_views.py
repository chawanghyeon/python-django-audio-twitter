from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble, Rebabble
from project.serializers import BabbleSerializer, RebabbleSerializer
from project.views.views_utils import (
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
        id = request.data.get("babble")

        if Rebabble.objects.filter(user=request.user, babble=id).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

        babble = Babble.objects.get_or_404(id=id)
        babble.rebabble_count += 1
        babble.save()

        Rebabble.objects.create(user=request.user, babble=babble)

        update_user_cache(request.user.id, id, "is_rebabbled", True)
        update_babble_cache(id, "rebabble_count", 1)

        return Response(
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        pk = int(pk)
        Rebabble.objects.filter(user=request.user, babble=pk).delete()
        Babble.objects.filter(id=pk).update(rebabble_count=F("rebabble_count") - 1)

        update_user_cache(request.user.id, pk, "is_rebabbled", False)
        update_babble_cache(pk, "rebabble_count", -1)

        return Response(
            status=status.HTTP_200_OK,
        )

    def list(self, request: HttpRequest) -> Response:
        user = get_user(request)

        babbles = Babble.objects.filter(rebabble__user=user).order_by("-created")
        serializer = BabbleSerializer(babbles, many=True)

        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return Response(serialized_data, status=status.HTTP_200_OK)
