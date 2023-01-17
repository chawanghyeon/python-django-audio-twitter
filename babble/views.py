import asyncio
from typing import Any, List, Optional, Type

from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.db.models.manager import BaseManager
from django.http import FileResponse, HttpRequest
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status, viewsets
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

    @action(detail=True, methods=["put"], url_name="password", url_path="password")
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
        babble: Babble = await Babble.objects.get(Babble, pk=pk)
        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )
        await babble.audio.open()
        return FileResponse(
            babble.audio,
            as_attachment=True,
            filename=babble.audio.name,
            status=status.HTTP_200_OK,
        )

    async def update(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        babble: Babble = await Babble.objects.get(Babble, pk=pk)
        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )
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
        babble: Babble = await Babble.objects.get(Babble, pk=pk)
        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )
        await babble.delete()
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
        comment: Comment = await Comment.objects.get(Comment, pk=pk)
        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
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
        comment: Comment = await Comment.objects.get(Comment, pk=pk)
        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        await comment.delete()
        return Response(
            {"message": "Comment deleted successfully"}, status=status.HTTP_200_OK
        )

    async def list(self, request: HttpRequest) -> Response:
        babble: Babble = await Babble.objects.get(user=request.user)
        comments: List[Comment] = await self.queryset.filter(babble=babble)
        serializer: CommentSerializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    async def retrieve(self, pk: Optional[int] = None) -> FileResponse:
        comment: Comment = await Comment.objects.get(Comment, pk=pk)
        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        await comment.audio.open()
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
        follower: Follower = await Follower.objects.get(Follower, pk=pk)
        if follower is None:
            return Response(
                {"error": "Follower not found"}, status=status.HTTP_404_NOT_FOUND
            )
        await follower.delete()
        return Response(
            {"message": "Follower deleted successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="followings")
    async def get_followings(self, request: HttpRequest) -> Response:
        follower: List[Follower] = await self.queryset.filter(follower=request.user)
        serializer: FollowerSerializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="followers")
    async def get_followers(self, request: HttpRequest) -> Response:
        follower: List[Follower] = await self.queryset.filter(following=request.user)
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
        like: Like = await Like.objects.get(Like, pk=pk)
        if like is None:
            return Response(
                {"error": "Like not found"}, status=status.HTTP_404_NOT_FOUND
            )
        await like.delete()
        return Response(
            {"message": "Like deleted successfully"}, status=status.HTTP_200_OK
        )


class TagViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Tag] = Tag.objects.all()
    serializer_class: Type[TagSerializer] = TagSerializer

    async def retrieve(self, pk: Optional[int] = None) -> Response:
        tag: Tag = await Tag.objects.get(Tag, pk=pk)
        if tag is None:
            return Response(
                {"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND
            )
        babbles: List[Babble] = await Babble.objects.filter(tags=tag)
        serializer: BabbleSerializer = BabbleSerializer(babbles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
