from re import S
from typing import Optional, Type

from django.core.cache import caches
from django.db import transaction
from django.db.models import F, Q
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..stt import STT

stt = STT()
user_cache = caches["default"]
babble_cache = caches["second"]


class BabbleViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    def save_keywords(self, babble: Babble) -> Babble:
        keywords = stt.get_keywords(babble.audio.path)
        tags = []

        for keyword in keywords:
            tag, _ = Tag.objects.get_or_create(text=keyword)
            tags.append(tag)

        babble.tags.add(*tags)
        babble.save()

        return babble

    def set_follower_cache(self, babble: Babble, user: User) -> None:
        followers = user.following.all()
        serializer = CacheBabbleSerializer(babble)

        for follower in followers:
            user_cache_data = user_cache.get(follower.id) or {}

            if user_cache_data.id in user_cache_data:
                del user_cache_data[id]

            user_cache_data[babble.id] = serializer.data

            if len(user_cache_data) > 20:
                user_cache_data.popitem(last=False)

            user_cache.set(follower.id, user_cache_data, 60 * 60 * 24 * 7)

    def set_rebabble_cache(self, rebabble: Babble, user: User) -> None:
        serializer = BabbleSerializer(rebabble)
        babble_cache.set(rebabble.id, serializer.data, 60 * 60 * 24 * 7)

        user_cache_data = user_cache.get(user.id)

        if user_cache_data and rebabble.id in user_cache_data:
            user_cache_data[rebabble.id]["rebabbled"] = True
            user_cache.set(user.id, user_cache_data, 60 * 60 * 24 * 7)

    def check_like_and_rebabble(
        self,
        followings_babble: BaseManager[Babble],
        user: User,
        serializer: CacheBabbleSerializer,
    ) -> CacheBabbleSerializer:
        babble_ids = [babble["id"] for babble in serializer.data]
        likes = Like.objects.filter(babble_id__in=babble_ids, user=user).values_list(
            "babble_id", flat=True
        )
        rebabbles = Babble.objects.filter(
            user=user, rebabble__in=followings_babble
        ).values_list("rebabble_id", flat=True)

        for babble in serializer.data:
            if babble["id"] in likes:
                babble["is_liked"] = True
            if babble["id"] in rebabbles:
                babble["is_rebabbled"] = True

        return serializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        serializer = BabbleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        babble = serializer.save(user=request.user)
        babble = self.save_keywords(babble)

        self.set_follower_cache(babble, request.user)

        serializer = BabbleSerializer(babble)
        babble_cache.set(babble.id, serializer.data, 60 * 60 * 24 * 7)

        if babble.rebabble:
            babble.rebabble.update(rebabble_count=F("rebabble_count") + 1)
            self.set_rebabble_cache(babble.rebabble, request.user)

        return Response(
            {"message": "Babble created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request: HttpRequest, id: Optional[int] = None) -> Response:
        babble_cache_data = babble_cache.get(id)

        if babble_cache_data:
            return Response(babble_cache_data, status=status.HTTP_200_OK)

        babble = Babble.objects.select_related("tags").get_or_404(id=id)

        serializer = BabbleSerializer(babble)
        babble_cache.set(id, serializer.data, 60 * 60 * 24 * 7)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request: HttpRequest, id: Optional[int] = None) -> Response:
        babble = Babble.objects.select_related("tags").get_or_404(id=id)

        serializer = BabbleSerializer(babble, data=request.data)
        serializer.is_valid(raise_exception=True)

        babble = serializer.save()
        babble.tags.clear()
        babble = self.save_keywords(babble)

        self.set_follower_cache(babble, request.user)

        return Response(
            {"message": "Babble updated successfully"}, status=status.HTTP_200_OK
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, id: Optional[int] = None) -> Response:
        babble = Babble.objects.select_related("rebabble").get_or_none(id=id)

        if babble.rebabble:
            babble.rebabble.update(rebabble_count=F("rebabble_count") - 1)

        babble.delete()
        babble_cache.delete(id)

        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest) -> Response:
        user_cache_data = user_cache.get(request.user.id)

        if user_cache_data:
            babbles = [
                babble_cache.get(id) or Babble.objects.get_or_none(id=id)
                for id in user_cache_data
            ]
            babbles = [babble for babble in babbles if babble is not None]
        else:
            babbles = Babble.objects.filter(
                Q(user__in=request.user.self.all().values_list("following", flat=True))
                | Q(user=request.user)
            ).order_by("-created")[:20]
            babbles_ids = [babble.id for babble in babbles]
            user_cache.set(request.user.id, babbles_ids, 60 * 60 * 24 * 7)

        serializer = BabbleSerializer(babbles, many=True)
        serializer = self.check_like_and_rebabble(babbles, request.user, serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)
