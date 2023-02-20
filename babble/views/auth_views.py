from typing import Any, Type

from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.db.models.manager import BaseManager
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..models import *
from ..serializers import *


class AuthViewSet(viewsets.GenericViewSet):
    queryset: BaseManager[User] = User.objects.all()
    serializer_class: Type[UserSerializer] = UserSerializer
    permission_classes: tuple = tuple()

    @action(detail=False, methods=["post"], url_name="signup")
    def signup(self, request: HttpRequest) -> Response:
        request.data["password"] = make_password(request.data.get("password"))
        serializer: UserSerializer = UserSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(
            {"message": "User created successfully"}, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["post"], url_name="signin")
    def signin(self, request: HttpRequest) -> Response:
        user: AbstractBaseUser | None = authenticate(
            username=request.data.get("username"), password=request.data.get("password")
        )

        if user == None:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer: UserSerializer = UserSerializer(user)
        token: Any = TokenObtainPairSerializer.get_token(user)

        return Response(
            {
                "user": serializer.data,
                "message": "Login successfully",
                "token": {"refresh": str(token), "access": str(token.access_token)},
            },
            status=status.HTTP_200_OK,
        )
