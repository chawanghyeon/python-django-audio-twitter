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
    def destroy(self, request: HttpRequest, id: Optional[str] = None) -> Response:
        id = int(id)
        Rebabble.objects.filter(user=request.user, babble=id).delete()
        Babble.objects.filter(id=id).update(rebabble_count=F("rebabble_count") - 1)

        update_user_cache(request.user.id, id, "is_rebabbled", False)
        update_babble_cache(id, "rebabble_count", -1)

        return Response(
            status=status.HTTP_200_OK,
        )

    def list(self, request: HttpRequest) -> Response:
        id = request.data.get("user")
        if id and id != request.user.id:
            user = User.objects.get_or_404(id=id)
        else:
            user = request.user

        babbles = Babble.objects.filter(rebabble__user=user).order_by("-created")
        serializer = BabbleSerializer(babbles, many=True)

        serialized_data = serializer.data
        serialized_data = check_rebabbled(serialized_data, user)
        serialized_data = check_liked(serialized_data, user)

        return Response(serialized_data, status=status.HTTP_200_OK)
