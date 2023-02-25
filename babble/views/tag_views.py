from typing import Optional

from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import *
from ..serializers import *


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(detail=False, methods=["get"], url_path="<str:tag>")
    def get_babbles_with_tag(
        self, request: HttpRequest, tag: Optional[str] = None
    ) -> Response:
        tags = Tag.objects.filter(name=tag)
        babbles = Babble.objects.filter(tags__in=tags)

        serializer = BabbleSerializer(babbles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
