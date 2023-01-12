import asyncio

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import FileResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .stt import STT

stt = STT()
try:
    stt.start()
except:
    stt = STT()
    stt.start()

# test
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    parser_classes = (MultiPartParser,)

    async def retrieve(self, request, pk=None):
        if pk is None:
            user = request.user
        else:
            user = await get_object_or_404(User, pk=pk)

        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    async def update(self, request):
        if request.data.image:
            request.data.image.name = request.user.id + "-" + "%y%m%d"

        serializer = UserSerializer(request.user, data=request.data)

        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "User updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, request):
        check = authenticate(
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

    @action(detail=True, methods=["post"], url_name="signup")
    async def signup(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.password = make_password(serializer.password)
            await serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_name="signin")
    async def signin(self, request):
        user = authenticate(
            username=request.data.get("username"), password=request.data.get("password")
        )

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=True, methods=["post"], url_name="logout")
    async def logout(self, request):
        await request.user.auth_token.delete()
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_name="password")
    async def update_password(self, request):
        user = request.user

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

    queryset = Babble.objects.all()
    serializer_class = BabbleSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    parser_classes = (MultiPartParser,)

    async def create(self, request):
        request.data["audio"].name = request.user.id + "-" + "%y%m%d"
        serializer = BabbleSerializer(data=request.data)
        # 오디오 분석 기능 추가
        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "Babble created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def retrieve(self, pk=None):
        babble = await get_object_or_404(Babble, pk=pk)
        await babble.audio.open()
        return FileResponse(
            babble.audio,
            as_attachment=True,
            filename=babble.audio.name,
            status=status.HTTP_200_OK,
        )

    async def update(self, request, pk=None):
        # 오디오 분석 기능 추가
        babble = await get_object_or_404(Babble, pk=pk)
        request.data["audio"].name = request.user.id + "-" + "%y%m%d"
        serializer = BabbleSerializer(babble, data=request.data)

        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "Babble updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, pk=None):
        await get_object_or_404(Babble, pk=pk).delete()
        return Response(
            {"message": "Babble deleted successfully"}, status=status.HTTP_200_OK
        )


class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    parser_classes = (MultiPartParser,)

    async def create(self, request):
        request.data["audio"].name = request.user.id + "-" + "%y%m%d"
        serializer = CommentSerializer(data=request.data)
        # 오디오 분석 기능 추가
        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "Comment created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def update(self, request, pk=None):
        # 오디오 분석 기능 추가
        comment = await get_object_or_404(Comment, pk=pk)
        request.data["audio"].name = request.user.id + "-" + "%y%m%d"
        serializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "Comment updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, pk=None):
        await get_object_or_404(Comment, pk=pk).delete()
        return Response(
            {"message": "Comment deleted successfully"}, status=status.HTTP_200_OK
        )

    async def list(self, request):
        babble = await Babble.objects.get(user=request.user)
        comments = await get_list_or_404(Comment, babble=babble)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    async def retrieve(self, pk=None):
        comment = await get_object_or_404(Comment, pk=pk)
        await comment.audio.open()
        return FileResponse(
            comment.audio,
            as_attachment=True,
            filename=comment.audio.name,
            status=status.HTTP_200_OK,
        )


class FollowerViewSet(viewsets.ModelViewSet):

    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    async def create(self, request):
        serializer = FollowerSerializer(data=request.data)

        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "Follower created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, pk=None):
        await get_object_or_404(Follower, pk=pk).delete()
        return Response(
            {"message": "Follower deleted successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], url_path="followings")
    async def get_followings(self, request):
        follower = await get_list_or_404(Follower, follower=request.user)
        serializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="followers")
    async def get_followers(self, request):
        follower = await get_list_or_404(Follower, following=request.user)
        serializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeViewSet(viewsets.ModelViewSet):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    async def create(self, request):
        serializer = LikeSerializer(data=request.data)

        if serializer.is_valid():
            await serializer.save()
            return Response(
                {"message": "Like created successfully"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def destroy(self, pk=None):
        await get_object_or_404(Like, pk=pk).delete()
        return Response(
            {"message": "Like deleted successfully"}, status=status.HTTP_200_OK
        )


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    @action(detail=True, methods=["get"])
    async def get_babbles_with_tag(self, pk=None):
        tag = await get_object_or_404(Tag, pk=pk)
        babbles = await get_list_or_404(Babble, tag=tag)
        serializer = BabbleSerializer(babbles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
