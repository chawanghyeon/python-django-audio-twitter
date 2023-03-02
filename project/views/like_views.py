from typing import Optional

from django.core.cache import caches
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble, Like, User
from project.serializers import BabbleSerializer, LikeSerializer
from project.views.views_utils import check_liked, check_rebabbled

user_cache = caches["default"]
babble_cache = caches["second"]


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @transaction.atomic
    def create(self, request: HttpRequest) -> Response:
        babble_id = request.data.get("babble")

        if Like.objects.filter(babble__pk=babble_id, user=request.user).exists():
            return Response(
                {"message": "Like already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(babble_id=babble_id, user=request.user)

        Babble.objects.filter(pk=babble_id).update(like_count=F("like_count") + 1)

        user_cache_data = user_cache.get(request.user.id)

        if user_cache_data:
            for data in user_cache_data:
                if data["id"] == babble_id:
                    data["is_liked"] = True
                    break

            user_cache.set(request.user.id, user_cache_data)

        babble_cache_data = babble_cache.get(babble_id)

        if babble_cache_data:
            babble_cache_data["like_count"] += 1
            babble_cache.set(babble_id, babble_cache_data)

        return Response(
            {"message": "Like created successfully"}, status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def destroy(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        Babble.objects.filter(pk=pk).update(like_count=F("like_count") - 1)
        Like.objects.filter(babble__pk=pk, user=request.user).delete()

        pk = int(pk)
        user_cache_data = user_cache.get(request.user.id)
        if user_cache_data:
            for data in user_cache_data:
                if data["id"] == pk:
                    data["is_liked"] = False
                    break

            user_cache.set(request.user.id, user_cache_data)

        babble_cache_data = babble_cache.get(pk)
        if babble_cache_data:
            babble_cache_data["like_count"] -= 1
            babble_cache.set(pk, babble_cache_data)

        return Response(
            {"message": "Like deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        if pk:
            user = User.objects.get_or_404(pk=pk)
        else:
            user = request.user

        babbles = Babble.objects.filter(like__user=user).order_by("-created")
        serializer = BabbleSerializer(babbles, many=True)
        check_rebabbled(serializer, user)
        check_liked(serializer, user)

        return Response(serializer.data, status=status.HTTP_200_OK)
