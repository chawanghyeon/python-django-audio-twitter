from typing import Any, Dict, List, Optional, Type

from django.core.cache import cache
from django.db import DatabaseError, transaction
from django.db.models import F
from django.db.models.manager import BaseManager
from django.http import FileResponse, HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..stt import STT

stt: STT = STT()


class BabbleViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    def create(self, request: HttpRequest) -> Response:
        serializer: BabbleSerializer = BabbleSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                babble: Babble = serializer.save(user=request.user)
                keywords: List[str] = stt.get_keywords(babble.audio.path)

                for keyword in keywords:
                    tag: Tag = Tag.objects.get_or_create(text=keyword)
                    babble.tags.add(tag)

                babble.save()

                followers: BaseManager[User] = request.user.following.all()
                serializer: CacheBabbleSerializer = CacheBabbleSerializer(babble)

                for follower in followers:
                    value: Any = cache.get(follower.id)
                    if value is None:
                        value = {}
                    value[serializer.data.get("id")] = serializer.data
                    if len(value) > 20:
                        value.popitem(last=False)
                    cache.set(follower.id, value, 60 * 60 * 24 * 7)

        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Babble created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request: HttpRequest, pk: Optional[int] = None) -> FileResponse:
        value: Any = cache.get(request.user.id)
        if value.get(pk) is not None:
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
                keywords: List[str] = stt.get_keywords(babble.audio.path)

                babble.tags.clear()

                for keyword in keywords:
                    tag: Tag = Tag.objects.get_or_create(text=keyword)
                    babble.tags.add(tag)

                babble.save()

                followers: BaseManager[User] = request.user.following.all()
                serializer: CacheBabbleSerializer = CacheBabbleSerializer(babble)

                for follower in followers:
                    value: Any = cache.get(follower.id)

                    if value is None:
                        value = {}

                    id: int = serializer.data.get("id")

                    if value.get(id) is not None:
                        del value[id]

                    value[id] = serializer.data
                    cache.set(follower.id, value, 60 * 60 * 24 * 7)
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
                    rebabble: Optional[Babble] = Babble.objects.get_or_none(
                        pk=babble.rebabble.id
                    )
                    if rebabble is None:
                        raise DatabaseError
                    rebabble.update(rebabble_count=F("rebabble_count") - 1)
                babble.delete()
        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        value: Any = cache.get(request.user.id)

        if value.get(pk) is not None:
            del value[pk]
            cache.set(request.user.id, value, 60 * 60 * 24 * 7)

        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest) -> Response:
        value: Any = cache.get(request.user.id)

        if value is not None:
            return Response(list(value), status=status.HTTP_200_OK)

        followings: BaseManager[User] = request.user.following.all()
        followings_babble: BaseManager[Babble] = Babble.objects.filter(
            user__in=followings
        ).order_by("-created_at")[-20:]

        serializer: CacheBabbleSerializer = CacheBabbleSerializer(
            followings_babble, many=True
        )

        likes: BaseManager[Like] = Like.objects.filter(
            babble__in=followings_babble, user=request.user
        )

        for like in likes:
            for babble in serializer.data:
                if babble.get("id") == like.babble.id:
                    babble["is_liked"] = True

        value: Dict[int, Any] = {}

        rebabbles: BaseManager[Babble] = Babble.objects.filter(
            user=request.user, rebabble__in=followings_babble
        )

        for rebabble in rebabbles:
            for babble in serializer.data:
                if babble.get("id") == rebabble.rebabble.id:
                    babble["is_rebabbled"] = True

        for babble in serializer.data:
            value[babble.get("id")] = babble

        cache.set(request.user.id, value, 60 * 60 * 24 * 7)

        return Response(serializer.data, status=status.HTTP_200_OK)
