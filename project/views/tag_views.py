from typing import Optional

from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.response import Response

from project.models import Babble, Tag
from project.serializers import BabbleSerializer, TagSerializer
from project.views.views_utils import check_liked, check_rebabbled


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        tag = Tag.objects.filter(text=pk)
        babbles = Babble.objects.filter(tags__in=tag).order_by("-created")

        serializer = BabbleSerializer(babbles, many=True)

        serialized_data = serializer.data
        serialized_data = check_rebabbled(serialized_data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return Response(serialized_data, status=status.HTTP_200_OK)
