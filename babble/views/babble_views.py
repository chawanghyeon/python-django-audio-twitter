from typing import Dict, List, Optional, Type

from django.core.cache import caches
from django.db import transaction
from django.db.models import F, Q
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..stt import STT

stt = STT()
user_cache = caches["default"]
babble_cache = caches["second"]

# user_cache.clear()
# babble_cache.clear()


class BabbleViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    def save_keywords(self, babble: Babble) -> Babble:
        keywords = stt.get_keywords(babble.audio.path)
        tags = []

        for keyword in keywords:
            tag = Tag.objects.get_or_create(text=keyword)
            tags.append(tag)

        babble.tags.add(*tags)
        babble.save()

        return babble

    def set_follower_cache(self, babble: Babble, user: User) -> None:
        followers = user.following.all()

        data_for_cache = {
            "id": babble.id,
            "is_rebabble": False,
            "is_like": False,
        }

        for follower in followers:
            user_cache_data = user_cache.get(follower.id) or []

            for data in user_cache_data:
                if data["id"] == babble.id:
                    if data["is_rebabble"]:
                        data_for_cache["is_rebabble"] = True
                    if data["is_like"]:
                        data_for_cache["is_like"] = True

                    user_cache_data.remove(data)
                    break

            user_cache_data.append(data_for_cache)

            if len(user_cache_data) > 20:
                user_cache_data.popitem(last=False)

            user_cache.set(follower.id, user_cache_data, 60 * 60 * 24 * 7)

    def check_like_and_rebabble(
        self,
        followings_babble: BaseManager[Babble],
        user: User,
        serializer: BabbleSerializer,
    ) -> BabbleSerializer:
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

    def get_babbles_from_cache(
        self, user_cache_data: List[Dict], user: User
    ) -> List[Babble]:
        cached_babbles = []
        non_cached_babbles = []

        for cached_babble in user_cache_data:
            babble = babble_cache.get(cached_babble["id"])
            if babble:
                if cached_babble["is_rebabbled"]:
                    babble["is_rebabbled"] = True
                if cached_babble["is_liked"]:
                    babble["is_liked"] = True
                cached_babbles.append(babble)
            else:
                non_cached_babbles.append(cached_babble["id"])

        non_cached_babbles = self.get_non_cached_babbles(non_cached_babbles, user)
        result = cached_babbles + non_cached_babbles
        result.sort(key=lambda x: x["created"], reverse=True)
        return result

    def get_non_cached_babbles(
        self, non_cached_babbles: List[int], user_cache_data: List[Dict]
    ) -> List[dict]:
        if not non_cached_babbles:
            return []

        babbles = Babble.objects.filter(id__in=non_cached_babbles).order_by("-created")
        serializer = BabbleSerializer(babbles, many=True)
        non_cached_babbles = serializer.data

        for babble in serializer.data:
            babble_cache.set(babble["id"], babble, 60 * 60 * 24 * 7)

        for babble in non_cached_babbles:
            for cached_babble in user_cache_data:
                if babble["id"] == cached_babble["id"]:
                    if cached_babble["is_rebabbled"]:
                        babble["is_rebabbled"] = True
                    if cached_babble["is_liked"]:
                        babble["is_liked"] = True
                    break

        return non_cached_babbles

    def get_babbles_from_db(self, user: User) -> List[Babble]:
        babbles = Babble.objects.filter(
            Q(user__in=user.self.all().values_list("following", flat=True))
            | Q(user=user)
        ).order_by("-created")[:20]

        serializer = BabbleSerializer(babbles, many=True)

        for babble in serializer.data:
            babble_cache.set(babble["id"], babble, 60 * 60 * 24 * 7)

        serializer = self.check_like_and_rebabble(babbles, user, serializer)

        data = []
        for babble in serializer.data:
            data.append(
                {
                    "id": babble["id"],
                    "is_rebabbled": babble["is_rebabbled"],
                    "is_liked": babble["is_liked"],
                }
            )

        user_cache.set(user.id, data, 60 * 60 * 24 * 7)

        return serializer.data

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
        babble.tags.clear()
        babble = self.save_keywords(babble)

        self.set_follower_cache(babble, request.user)

        return Response(
            {"message": "Babble updated successfully"}, status=status.HTTP_200_OK
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        babble = Babble.objects.select_related("rebabble").get(pk=pk)

        if babble.rebabble:
            babble.rebabble.update(rebabble_count=F("rebabble_count") - 1)

        babble.delete()
        babble_cache.delete(pk)

        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest) -> Response:
        user_cache_data = user_cache.get(request.user.id)

        if user_cache_data:
            babbles = self.get_babbles_from_cache(user_cache_data, request.user)
        else:
            babbles = self.get_babbles_from_db(request.user)

        return Response(babbles, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="rebabble")
    def create_rebabble(
        self, request: HttpRequest, pk: Optional[str] = None
    ) -> Response:
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
