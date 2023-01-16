import asyncio
from lib2to3.pgen2 import token
from typing import Any, List, Optional, Type
from urllib import response

from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.db.models.manager import BaseManager
from django.http import FileResponse, HttpRequest
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import *
from .serializers import *
from .stt import STT

stt: STT = STT()


class AuthViewSet(viewsets.GenericViewSet):
    queryset: BaseManager[User] = User.objects.all()
    serializer_class: Type[UserSerializer] = UserSerializer

    @action(detail=False, methods=["post"], url_name="signup")
    async def signup(self, request: HttpRequest) -> Response:
        serializer: UserSerializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.password = make_password(serializer.password)
            await serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_name="signin")
    async def signin(self, request: HttpRequest) -> Response:
        user: AbstractBaseUser | None = authenticate(
            username=request.data.get("username"), password=request.data.get("password")
        )

        if user:
            token: Any = TokenObtainPairSerializer.get_token(user)
            refresh_token: str = str(token)
            access_token: str = str(token.access_token)
            response: Response = Response(
                {
                    "User": user,
                    "message": "Login successfully",
                    "token": {"refresh": refresh_token, "access": access_token},
                },
                status=status.HTTP_200_OK,
            )
            response.set_cookie(key="refresh_token", value=refresh_token)
            response.set_cookie(key="access_token", value=access_token)
            return response

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=["post"], url_name="logout")
    async def logout(self, request: HttpRequest) -> Response:
        await request.user.auth_token.delete()
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_name="password")
    async def update_password(self, request: HttpRequest) -> Response:
        user: AbstractBaseUser | AnonymousUser = request.user

        if user.check_password(request.data.get("old_password")):
            user.password = make_password(request.data.get("new_password"))
            await user.save()
            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED
        )


class UserViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[User] = User.objects.all()
    serializer_class: Type[UserSerializer] = UserSerializer

    async def retrieve(
        self, request: HttpRequest, pk: Optional[int] = None
    ) -> Response:
        if pk is None:
            user: AbstractBaseUser | AnonymousUser = request.user
        else:
            user: User = await User.objects.get(pk=pk)

        if user:
            serializer: UserSerializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    async def update(self, request: HttpRequest) -> Response:
        if request.data.image:
            request.data.image.name = str(request.user.id) + "-" + "%y%m%d"

        serializer: UserSerializer = UserSerializer(request.user, data=request.data)

        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "User updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, request: HttpRequest) -> Response:
        check: AbstractBaseUser | None = authenticate(
            username=request.user.username, password=request.data.get("password")
        )

        if check:
            await request.user.delete()
            return Response(
                {"message": "User deleted successfully"}, status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED
        )


class BabbleViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    async def create(self, request: HttpRequest) -> Response:
        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: BabbleSerializer = BabbleSerializer(data=request.data)
        if serializer.is_valid():
            await serializer.save()
            serializer.data.tags = stt.get_keywords(serializer.data.audio)
            await serializer.save()
            return Response(
                {"message": "Babble created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def retrieve(self, pk: Optional[int] = None) -> FileResponse:
        babble: Babble = get_object_or_404(Babble, pk=pk)
        babble.audio.open()
        return FileResponse(
            babble.audio,
            as_attachment=True,
            filename=babble.audio.name,
            status=status.HTTP_200_OK,
        )

    async def update(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        babble: Babble = get_object_or_404(Babble, pk=pk)
        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: BabbleSerializer = BabbleSerializer(babble, data=request.data)

        if serializer.is_valid():
            await serializer.save()
            serializer.data.tags = stt.get_keywords(serializer.data.audio)
            await serializer.save()
            return Response(
                {"message": "Babble updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, pk: Optional[int] = None) -> Response:
        get_object_or_404(Babble, pk=pk).delete()
        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )


class CommentViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Comment] = Comment.objects.all()
    serializer_class: Type[CommentSerializer] = CommentSerializer

    async def create(self, request: HttpRequest) -> Response:
        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: CommentSerializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            await serializer.save()
            serializer.data.tags = stt.get_keywords(serializer.data.audio)
            await serializer.save()
            return Response(
                {"message": "Comment created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def update(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        comment: Comment = get_object_or_404(Comment, pk=pk)
        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: CommentSerializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid():
            await serializer.save()
            serializer.data.tags = stt.get_keywords(serializer.data.audio)
            await serializer.save()
            return Response(
                {"message": "Comment updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, pk: Optional[int] = None) -> Response:
        get_object_or_404(Comment, pk=pk).delete()
        return Response(
            {"message": "Comment deleted successfully"}, status=status.HTTP_200_OK
        )

    async def list(self, request: HttpRequest) -> Response:
        babble: Babble = Babble.objects.get(user=request.user)
        comments: List[Comment] = get_list_or_404(Comment, babble=babble)
        serializer: CommentSerializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    async def retrieve(self, pk: Optional[int] = None) -> FileResponse:
        comment: Comment = get_object_or_404(Comment, pk=pk)
        comment.audio.open()
        return FileResponse(
            comment.audio,
            as_attachment=True,
            filename=comment.audio.name,
            status=status.HTTP_200_OK,
        )


class FollowerViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Follower] = Follower.objects.all()
    serializer_classz: Type[FollowerSerializer] = FollowerSerializer

    async def create(self, request: HttpRequest) -> Response:
        serializer: FollowerSerializer = FollowerSerializer(data=request.data)

        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "Follower created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, pk: Optional[int] = None) -> Response:
        get_object_or_404(Follower, pk=pk).delete()
        return Response(
            {"message": "Follower deleted successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="followings")
    async def get_followings(self, request: HttpRequest) -> Response:
        follower: List[Follower] = get_list_or_404(Follower, follower=request.user)
        serializer: FollowerSerializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="followers")
    async def get_followers(self, request: HttpRequest) -> Response:
        follower: List[Follower] = get_list_or_404(Follower, following=request.user)
        serializer: FollowerSerializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Like] = Like.objects.all()
    serializer_class: Type[LikeSerializer] = LikeSerializer

    async def create(self, request: HttpRequest) -> Response:
        serializer: LikeSerializer = LikeSerializer(data=request.data)

        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "Like created successfully"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, pk: Optional[int] = None) -> Response:
        get_object_or_404(Like, pk=pk).delete()
        return Response(
            {"message": "Like deleted successfully"}, status=status.HTTP_200_OK
        )


class TagViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Tag] = Tag.objects.all()
    serializer_class: Type[TagSerializer] = TagSerializer

    @action(detail=False, methods=["get"])
    async def get_babbles_with_tag(self, pk: Optional[int] = None) -> Response:
        tag: Tag = get_object_or_404(Tag, pk=pk)
        babbles: List[Babble] = get_list_or_404(Babble, tag=tag)
        serializer: BabbleSerializer = BabbleSerializer(babbles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
