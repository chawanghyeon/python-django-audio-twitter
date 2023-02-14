from typing import List, Optional, Type

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

        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: BabbleSerializer = BabbleSerializer(babble, data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                serializer.save()
                serializer.data["tags"] = stt.get_keywords(serializer.data.get("audio"))
                serializer.save()
        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Babble updated successfully"}, status=status.HTTP_200_OK
        )

    def destroy(self, pk: Optional[int] = None) -> Response:
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

        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )
