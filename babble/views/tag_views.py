from typing import List, Optional, Type

from django.db.models.manager import BaseManager
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class TagViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Tag] = Tag.objects.all()
    serializer_class: Type[TagSerializer] = TagSerializer

    @action(detail=False, methods=["get"], url_path="<str:tag>")
    def get_babbles_with_tag(
        self, request: HttpRequest, tag: Optional[str] = None
    ) -> Response:
        tags: List[Tag] = self.queryset.filter(text=tag)

        if tags is None:
            return Response(
                {"error": "Tags not found"}, status=status.HTTP_404_NOT_FOUND
            )

        babbles: List[Babble] = Babble.objects.filter(tags=tags)
        serializer: BabbleSerializer = BabbleSerializer(babbles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
