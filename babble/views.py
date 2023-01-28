from typing import Any, List, Optional, Type

from django.contrib.auth import authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.db import DatabaseError, transaction
from django.db.models import F, Q
from django.db.models.manager import BaseManager
from django.http import FileResponse, HttpRequest
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
    permission_classes: tuple = tuple()

    @action(detail=False, methods=["post"], url_name="signup")
    def signup(self, request: HttpRequest) -> Response:
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


class UserViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[User] = User.objects.all()
    serializer_class: Type[UserSerializer] = UserSerializer

    def retrieve(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        user: User = User.objects.get(pk=pk)

        if user == None:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer: UserSerializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request: HttpRequest) -> Response:
        if request.data["image"]:
            request.data["image"].name = str(request.user.id) + "-" + "%y%m%d"

        serializer: UserSerializer = UserSerializer(request.user, data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(
            {"message": "User updated successfully"}, status=status.HTTP_200_OK
        )

    def destroy(self, request: HttpRequest) -> Response:
        check: AbstractBaseUser | None = authenticate(
            username=request.user.username, password=request.data.get("password")
        )

        if check == None:
            return Response(
                {"error": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            with transaction.atomic():
                User.objects.filter(follower__user=check).update(
                    followers=F("followers") - 1
                )
                User.objects.filter(follower__following=check).update(
                    following=F("following") - 1
                )
                check.delete()

            return Response(
                {"message": "User deleted successfully"}, status=status.HTTP_200_OK
            )
        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["put"], url_name="password", url_path="password")
    def update_password(self, request: HttpRequest) -> Response:
        user: AbstractBaseUser | AnonymousUser = request.user

        if user.check_password(request.data.get("old_password")) == False:
            return Response(
                {"error": "Wrong password"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user.password = make_password(request.data.get("new_password"))
        user.save()
        return Response(
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )


class BabbleViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Babble] = Babble.objects.all()
    serializer_class: Type[BabbleSerializer] = BabbleSerializer

    def create(self, request: HttpRequest) -> Response:
        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: BabbleSerializer = BabbleSerializer(data=request.data)
        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        serializer.data["tags"] = stt.get_keywords(serializer.data.get("audio"))
        serializer.save()
        return Response(
            {"message": "Babble created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, pk: Optional[int] = None) -> FileResponse:
        babble: Babble = Babble.objects.get(Babble, pk=pk)
        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )

        babble.audio.open()

        return FileResponse(
            babble.audio,
            as_attachment=True,
            filename=babble.audio.name,
            status=status.HTTP_200_OK,
        )

    def update(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        babble: Babble = Babble.objects.get(Babble, pk=pk)
        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )
        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: BabbleSerializer = BabbleSerializer(babble, data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        serializer.data["tags"] = stt.get_keywords(serializer.data.get("audio"))
        serializer.save()
        return Response(
            {"message": "Babble updated successfully"}, status=status.HTTP_200_OK
        )

    def destroy(self, pk: Optional[int] = None) -> Response:
        babble: Babble = Babble.objects.get(Babble, pk=pk)
        if babble is None:
            return Response(
                {"error": "Babble not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                if babble.rebabble != None:
                    Babble.objects.get(Babble, pk=babble.rebabble.id).update(
                        rebabble_count=F("rebabble_count") - 1
                    )
                babble.delete()
        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Comment] = Comment.objects.all()
    serializer_class: Type[CommentSerializer] = CommentSerializer

    def create(self, request: HttpRequest) -> Response:
        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: CommentSerializer = CommentSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                serializer.save()
                serializer.data["tags"] = stt.get_keywords(serializer.data.get("audio"))
                serializer.save()

                babble: Babble = Babble.objects.get(
                    Babble, pk=request.data.get("babble")
                )
                babble.comment_count += 1
                babble.save()
        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Comment created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        comment: Comment = Comment.objects.get(Comment, pk=pk)

        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        request.data["audio"].name = str(request.user.id) + "-" + "%y%m%d"
        serializer: CommentSerializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        serializer.data["tags"] = stt.get_keywords(serializer.data.get("audio"))
        serializer.save()

        return Response(
            {"message": "Comment updated successfully"}, status=status.HTTP_200_OK
        )

    def destroy(self, pk: Optional[int] = None) -> Response:
        comment: Comment = Comment.objects.get(Comment, pk=pk)
        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            with transaction.atomic():
                babble: Babble = Babble.objects.get(Babble, pk=comment.babble.id)
                babble.comment_count -= 1
                babble.save()
                comment.delete()
        except DatabaseError:
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {"message": "Comment deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest) -> Response:
        babble: Babble = Babble.objects.get(user=request.user)
        comments: List[Comment] = self.queryset.filter(babble=babble)
        serializer: CommentSerializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, pk: Optional[int] = None) -> FileResponse:
        comment: Comment = Comment.objects.get(Comment, pk=pk)

        if comment is None:
            return Response(
                {"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )
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

    def create(self, request: HttpRequest) -> Response:
        serializer: FollowerSerializer = FollowerSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                serializer.save()
                user: User = User.objects.get(User, pk=request.data.get("user"))
                following: User = User.objects.get(
                    User, pk=request.data.get("following")
                )
                user.following += 1
                following.followers += 1
                user.save()
                following.save()
        except DatabaseError:
            return Response(
                {"error": "Cancle follower"}, status=status.HTTP_409_CONFLICT
            )

        return Response(
            {"message": "Follower created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, pk: Optional[int] = None) -> Response:
        following: User = User.objects.get(User, pk=pk)
        follower: Follower = Follower.objects.get(
            Follower, User=request.user, following=following
        )
        if follower is None:
            return Response(
                {"error": "Follower not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            with transaction.atomic():
                follower.delete()
                request.user.following -= 1
                following.followers -= 1
                request.user.save()
                following.save()
        except DatabaseError:
            return Response(
                {"error": "Cancle follower"}, status=status.HTTP_409_CONFLICT
            )

        return Response(
            {"message": "Follower deleted successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="followings")
    def get_followings(self, request: HttpRequest) -> Response:
        follower: List[Follower] = self.queryset.filter(follower=request.user)
        serializer: FollowerSerializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="followers")
    def get_followers(self, request: HttpRequest) -> Response:
        follower: List[Follower] = self.queryset.filter(following=request.user)
        serializer: FollowerSerializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Like] = Like.objects.all()
    serializer_class: Type[LikeSerializer] = LikeSerializer

    def create(self, request: HttpRequest) -> Response:
        serializer: LikeSerializer = LikeSerializer(data=request.data)

        if serializer.is_valid() == False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                serializer.save()
                babble: Babble = Babble.objects.get(
                    Babble, pk=request.data.get("babble")
                )
                babble.like_count += 1
                babble.save()
                serializer.save()
        except DatabaseError:
            return Response({"error": "Cancle like"}, status=status.HTTP_409_CONFLICT)

        return Response(
            {"message": "Like created successfully"}, status=status.HTTP_201_CREATED
        )

    def destroy(self, pk: Optional[int] = None) -> Response:
        like: Like = Like.objects.get(Like, pk=pk)
        if like is None:
            return Response(
                {"error": "Like not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
                babble: Babble = Babble.objects.get(Babble, pk=like.babble.id)
                babble.like_count -= 1
                babble.save()
                like.delete()
        except DatabaseError:
            return Response({"error": "Cancle unlike"}, status=status.HTTP_409_CONFLICT)

        return Response(
            {"message": "Like deleted successfully"}, status=status.HTTP_200_OK
        )

    def list(self, request: HttpRequest, id: Optional[int] = None) -> Response:
        user: User = User.objects.get(User, pk=id)

        if user is None:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        likes: List[Like] = self.queryset.filter(user=user)
        serializer: LikeSerializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):

    queryset: BaseManager[Tag] = Tag.objects.all()
    serializer_class: Type[TagSerializer] = TagSerializer

    @action(detail=False, methods=["get"], url_path="<str:tag>")
    def get_babbles_with_tag(self, tag: Optional[str] = None) -> Response:
        tags: List[Tag] = self.queryset.filter(text=tag)

        if tags is None:
            return Response(
                {"error": "Tags not found"}, status=status.HTTP_404_NOT_FOUND
            )

        babbles: List[Babble] = Babble.objects.filter(tags=tags)
        serializer: BabbleSerializer = BabbleSerializer(babbles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
