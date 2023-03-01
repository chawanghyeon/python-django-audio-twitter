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
    def create(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        Rebabble.objects.create(user=request.user, babble=pk)
        Babble.objects.get(pk=pk).update(rebabble_count=F("rebabble_count") + 1)

        user_cache_data = user_cache.get(request.user.id)

        if user_cache_data and pk in user_cache_data:
            user_cache_data[pk]["rebabbled"] = True
            user_cache.set(request.user.id, user_cache_data, 60 * 60 * 24 * 7)

        return Response(
            {"message": "Rebabble created successfully"},
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        Rebabble.objects.get(user=request.user, babble=pk).delete()
        Babble.objects.get(pk=pk).update(rebabble_count=F("rebabble_count") - 1)

        user_cache_data = user_cache.get(request.user.id)

        if user_cache_data and pk in user_cache_data:
            user_cache_data[pk]["rebabbled"] = False
            user_cache.set(request.user.id, user_cache_data, 60 * 60 * 24 * 7)

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
