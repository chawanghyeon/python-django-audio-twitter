from typing import Optional, Type

from django.core.cache import caches
from django.db import transaction
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble, Like, Rebabble
from project.serializers import BabbleSerializer
from project.views.views_utils import (
    get_babbles_from_cache,
    get_babbles_from_db,
    save_keywords,
    set_caches,
    set_follower_cache,
)

user_cache = caches["default"]
babble_cache = caches["second"]

user_cache.clear()
babble_cache.clear()


class BabbleViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        serializer = BabbleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        babble = serializer.save(user=request.user)
        babble = save_keywords(babble)

        serializer = BabbleSerializer(babble)

        set_caches(babble, request.user, serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble_data = babble_cache.get(pk)

        if babble_data is None:
            babble = Babble.objects.get(pk=pk)
            babble_data = BabbleSerializer(babble).data
            babble_cache.set(pk, babble_data)

        is_rebabbled = Rebabble.objects.filter(user=request.user, babble=pk).exists()
        is_liked = Like.objects.filter(user=request.user, babble=pk).exists()

        babble_data["is_rebabbled"] = is_rebabbled
        babble_data["is_liked"] = is_liked

        return Response(babble_data, status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble = Babble.objects.get_or_404(pk=pk)
        serializer = BabbleSerializer(babble, data=request.data)
        serializer.is_valid(raise_exception=True)
        babble = serializer.save()

        babble = save_keywords(babble)

        set_follower_cache(babble, request.user)

        return Response(BabbleSerializer(babble).data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        Babble.objects.filter(pk=pk).delete()
        babble_cache.delete(pk)

        return Response(status=status.HTTP_200_OK)

    def list(self, request: HttpRequest) -> Response:
        user_cache_data = user_cache.get(request.user.pk)

        if user_cache_data:
            babbles = get_babbles_from_cache(user_cache_data, request.user)
        else:
            babbles = get_babbles_from_db(request.user)

        return Response(babbles, status=status.HTTP_200_OK)
