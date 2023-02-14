from typing import Any, List, Optional, Type

from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.db import DatabaseError, transaction
from django.db.models import F, Q
from django.db.models.manager import BaseManager
from django.http import FileResponse, HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..models import *
from ..serializers import *
from ..stt import STT

stt: STT = STT()


class TagViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Tag] = Tag.objects.all()
    serializer_class: Type[TagSerializer] = TagSerializer

    @action(detail=False, methods=["get"], url_path="<str:tag>")
    def get_babbles_with_tag(self, tag: Optional[str] = None) -> Response:
        tags: List[Tag] = self.queryset.filter(text=tag)

        if tags is None:
            return Response(
                {"error": "Tags not found"}, status=status.HTTP_404_NOT_FOUND
            )

        babbles: List[Babble] = Babble.objects.filter(tags=tags)
        serializer: BabbleSerializer = BabbleSerializer(babbles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
