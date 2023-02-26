from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..models import *
from ..serializers import *


class AuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = tuple()

    @action(detail=False, methods=["post"], url_name="signup")
    def signup(self, request: HttpRequest) -> Response:
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(password=make_password(request.data.get("password")))
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_name="signin")
    def signin(self, request: HttpRequest) -> Response:
        data = {
            "username": request.data.get("username"),
            "password": request.data.get("password"),
        }

        token = TokenObtainPairSerializer().validate(data)
        user = authenticate(**data)
        serializer = UserSerializer(user)

        return Response(
            {
                "user": serializer.data,
                "message": "Login successfully",
                "token": {"refresh": token["refresh"], "access": token["access"]},
            },
            status=status.HTTP_200_OK,
        )
