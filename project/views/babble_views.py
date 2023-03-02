from typing import Optional, Type

from django.core.cache import caches
from django.db import transaction
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble
from project.serializers import BabbleSerializer
from project.views.views_utils import (
    get_babbles_from_cache,
    get_babbles_from_db,
    save_keywords,
    set_follower_cache,
)

user_cache = caches["default"]
babble_cache = caches["second"]


class BabbleViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        serializer = BabbleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        babble = serializer.save(user=request.user)
        babble = save_keywords(babble)

        set_follower_cache(babble, request.user)

        serializer = BabbleSerializer(babble)
        babble_cache.set(babble.id, serializer.data, 60 * 60 * 24 * 7)

        return Response(
            {"message": "Babble created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble_cache_data = babble_cache.get(pk)

        if babble_cache_data:
            return Response(babble_cache_data, status=status.HTTP_200_OK)

        babble = Babble.objects.get(pk=pk)
        serializer = BabbleSerializer(babble)

        babble_cache.set(pk, serializer.data, 60 * 60 * 24 * 7)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble = Babble.objects.get_or_404(pk=pk)

        serializer = BabbleSerializer(babble, data=request.data)
        serializer.is_valid(raise_exception=True)

        babble = serializer.save()
        babble = save_keywords(babble)

        set_follower_cache(babble, request.user)

        return Response(
            {"message": "Babble updated successfully"}, status=status.HTTP_200_OK
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        Babble.objects.get(pk=pk).delete()
        babble_cache.delete(pk)

        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest) -> Response:
        user_cache_data = user_cache.get(request.user.id)

        if user_cache_data:
            babbles = get_babbles_from_cache(user_cache_data, request.user)
        else:
            babbles = get_babbles_from_db(request.user)

        return Response(babbles, status=status.HTTP_200_OK)
