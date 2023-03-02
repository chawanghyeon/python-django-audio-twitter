from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import *
from ..serializers import *

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
                {"message": "Rebabble already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        babble = Babble.objects.get_or_404(pk=pk)
        Rebabble.objects.create(user=request.user, babble=babble)
        babble.rebabble_count = F("rebabble_count") + 1
        babble.save(update_fields=["rebabble_count"])

        user_cache_data = user_cache.get(request.user.id)
        if user_cache_data:
            for data in user_cache_data:
                if data["id"] == pk:
                    data["is_rebabbled"] = True
                    break
            user_cache.set(request.user.id, user_cache_data, 60 * 60 * 24 * 7)

        babble_cache_data = babble_cache.get(pk)
        if babble_cache_data:
            babble_cache_data["rebabble_count"] += 1
            babble_cache.set(pk, babble_cache_data, 60 * 60 * 24 * 7)

        return Response(
            {"message": "Rebabble created successfully"},
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        pk = int(pk)
        Rebabble.objects.get(user=request.user, babble=pk).delete()
        Babble.objects.filter(pk=pk).update(rebabble_count=F("rebabble_count") - 1)

        user_cache_data = user_cache.get(request.user.id)
        if user_cache_data:
            for data in user_cache_data:
                if data["id"] == pk:
                    data["is_rebabbled"] = False
                    break
            user_cache.set(request.user.id, user_cache_data, 60 * 60 * 24 * 7)

        babble_cache_data = babble_cache.get(pk)
        if babble_cache_data:
            babble_cache_data["rebabble_count"] -= 1
            babble_cache.set(pk, babble_cache_data, 60 * 60 * 24 * 7)

        return Response(
            {"message": "Rebabble deleted successfully"},
            status=status.HTTP_200_OK,
        )

    def list(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        if pk:
            user = User.objects.get_or_404(pk=pk)
        else:
            user = request.user

        rebabbles = Rebabble.objects.filter(user=user).values_list("babble", flat=True)
        serializer = BabbleSerializer(rebabbles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)