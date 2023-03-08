from typing import Optional

from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from project.models import Babble, Tag
from project.serializers import BabbleSerializer, TagSerializer
from project.views.views_utils import check_liked, check_rebabbled


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def retrieve(self, request: HttpRequest, pk: Optional[str] = None) -> Response:
        pagenator = CursorPagination()
        tag = Tag.objects.filter(text=pk)
        babbles = Babble.objects.filter(tags__in=tag)

        babbles = pagenator.paginate_queryset(babbles, request)

        if babbles is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BabbleSerializer(babbles, many=True)
<<<<<<< HEAD

=======
>>>>>>> bf6b529 (Add paginate logic)
        serialized_data = check_rebabbled(serializer.data, request.user)
        serialized_data = check_liked(serialized_data, request.user)

        return pagenator.get_paginated_response(serialized_data)
