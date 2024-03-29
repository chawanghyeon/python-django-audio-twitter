from typing import Optional

from django.http import Http404, HttpRequest
from rest_framework import viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from babbles.models import Babble
from babbles.serializers import BabbleSerializer
from tags.models import Tag
from tags.serializers import TagSerializer
from tags.utils import check_liked, check_rebabbled


class TagViewSet(viewsets.ViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        pagenator = CursorPagination()
        tag = Tag.objects.filter(text=pk)
        query = Babble.objects.filter(tags__in=tag)
        query = pagenator.paginate_queryset(query, request)

        if query is None:
            raise Http404

        serializer = BabbleSerializer(query, many=True)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return pagenator.get_paginated_response(serialized_data)
