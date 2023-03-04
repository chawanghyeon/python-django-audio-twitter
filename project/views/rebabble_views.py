from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble, Rebabble, User
from project.serializers import BabbleSerializer, RebabbleSerializer
from project.views.views_utils import (
    check_liked,
    check_rebabbled,
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
        pk = request.data.get("babble")

        if Rebabble.objects.filter(user=request.user, babble=pk).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

        babble = Babble.objects.get_or_404(pk=pk)
        babble.rebabble_count += 1
        babble.save()

        Rebabble.objects.create(user=request.user, babble=babble)

        update_user_cache(request.user.pk, pk, "is_rebabbled", True)
        update_babble_cache(pk, "rebabble_count", 1)

        return Response(
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        pk = int(pk)
        Rebabble.objects.filter(user=request.user, babble=pk).delete()
        Babble.objects.filter(pk=pk).update(rebabble_count=F("rebabble_count") - 1)

        update_user_cache(request.user.pk, pk, "is_rebabbled", False)
        update_babble_cache(pk, "rebabble_count", -1)

        return Response(
            status=status.HTTP_200_OK,
        )

    def list(self, request: HttpRequest) -> Response:
        pk = request.data.get("user")
        if pk and pk != request.user.pk:
            user = User.objects.get_or_404(pk=pk)
        else:
            user = request.user

        babbles = Babble.objects.filter(rebabble__user=user).order_by("-created")
        serializer = BabbleSerializer(babbles, many=True)

        serialized_data = serializer.data
        serialized_data = check_rebabbled(serialized_data, user)
        serialized_data = check_liked(serialized_data, user)

        return Response(serialized_data, status=status.HTTP_200_OK)
