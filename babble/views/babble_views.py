from typing import Any, Dict, List, Optional, Type

from django.core.cache import caches
from django.core.cache.backends.base import BaseCache
from django.db import DatabaseError, transaction
from django.db.models import F, Q
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..stt import STT

stt: STT = STT()
user_cache: BaseCache = caches["default"]
babble_cache: BaseCache = caches["pymemcache"]


class BabbleViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    def save_keywords(self, babble: Babble) -> Babble:
        keywords: List[str] = stt.get_keywords(babble.audio.path)

        for keyword in keywords:
            tag: Tag = Tag.objects.get_or_create(text=keyword)
            babble.tags.add(tag)

        babble.save()

        return babble

    def set_follower_cache(self, babble: Babble, user: User) -> None:
        followers: BaseManager[User] = user.following.all()
        serializer: CacheBabbleSerializer = CacheBabbleSerializer(babble)

        for follower in followers:
            value: Dict = user_cache.get(follower.id)

            if value is None:
                value = {}

            if value.get(id) is not None:
                del value[id]

            value[babble.id] = serializer.data

            if len(value) > 20:
                value.popitem(last=False)

            user_cache.set(follower.id, value, 60 * 60 * 24 * 7)

    def set_rebabble_cache(self, rebabble: Babble, user: User) -> None:
        serializer: BabbleSerializer = BabbleSerializer(rebabble)

        babble_cache.set(rebabble.id, serializer.data, 60 * 60 * 24 * 7)

        value: Dict = user_cache.get(user.id)

        if value.get(rebabble.id) is not None:
            value[rebabble.id]["rebabbled"] = True

    def check_like_and_rebabble(
        self,
        followings_babble: BaseManager[Babble],
        user: User,
        serializer: CacheBabbleSerializer,
    ) -> CacheBabbleSerializer:
        likes: BaseManager[Like] = Like.objects.filter(
            babble__in=followings_babble, user=user
        )

        for like in likes:
            for babble in serializer.data:
                if babble.get("id") == like.babble.id:
                    babble["is_liked"] = True

        rebabbles: BaseManager[Babble] = Babble.objects.filter(
            user=user, rebabble__in=followings_babble
        )

        for rebabble in rebabbles:
            for babble in serializer.data:
                if babble.get("id") == rebabble.rebabble.id:
                    babble["is_rebabbled"] = True

        return serializer

    def create(self, request: HttpRequest) -> Response:
        serializer: BabbleSerializer = BabbleSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                babble: Babble = serializer.save(user=request.user)
                babble = self.save_keywords(babble)

                serializer: BabbleSerializer = BabbleSerializer(babble)
                babble_cache.set(babble.id, serializer.data, 60 * 60 * 24 * 7)

                self.set_follower_cache(babble, request.user)

                if babble.rebabble != None:
                    rebabble: Babble = babble.rebabble
                    rebabble.update(rebabble_count=F("rebabble_count") + 1)

                    self.set_rebabble_cache(rebabble, request.user)

        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Babble created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        value: Any = user_cache.get(request.user.id)

        if value is not None and value.get(pk) is not None:
            return Response(value.get(pk), status=status.HTTP_200_OK)

        babble: Optional[Babble] = Babble.objects.get_or_none(pk=pk)

        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer: BabbleSerializer = BabbleSerializer(babble)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        babble: Optional[Babble] = Babble.objects.get_or_none(pk=pk)

        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer: BabbleSerializer = BabbleSerializer(babble, data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                babble: Babble = serializer.save()
                babble.tags.clear()
                babble = self.save_keywords(babble)

                self.set_follower_cache(babble, request.user)

        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Babble updated successfully"}, status=status.HTTP_200_OK
        )

    def destroy(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        babble: Optional[Babble] = Babble.objects.get_or_none(pk=pk)

        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                if babble.rebabble != None:
                    babble.rebabble.update(rebabble_count=F("rebabble_count") - 1)

                babble.delete()

        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        value: Any = babble_cache.get(babble.id)

        babble_cache.set(babble.id, value, 60 * 60 * 24 * 7)

        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest) -> Response:
        value: Any = user_cache.get(request.user.id)

        if value is not None:
            babbles: list[Any] = []
            for id in value.values():
                if babble_cache.get(id) is not None:
                    babbles.append(babble_cache.get(id))
                    continue
                babble: Optional[Babble] = Babble.objects.get_or_none(pk=id)
                if babble is None:
                    continue
                serializer: BabbleSerializer = BabbleSerializer(babble)
                babbles.append(serializer.data)
                babble_cache.set(babble.id, serializer.data, 60 * 60 * 24 * 7)

            serializer: BabbleSerializer = BabbleSerializer(babbles, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        followings_babble: BaseManager[Babble] = Babble.objects.filter(
            Q(user__in=request.user.self.followings.all()) | Q(user=request.user)
        ).order_by("-created")[:20]

        serializer: CacheBabbleSerializer = CacheBabbleSerializer(
            followings_babble, many=True
        )

        serializer = self.check_like_and_rebabble(
            followings_babble, request.user, serializer
        )

        value: Dict[int, Any] = {}

        for data in serializer.data:
            value[data.get("id")] = data

        user_cache.set(request.user.id, value, 60 * 60 * 24 * 7)

        return Response(serializer.data, status=status.HTTP_200_OK)
