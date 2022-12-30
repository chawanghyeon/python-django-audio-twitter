from .serializers import *
from .models import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrReadOnly
from rest_framework.parsers import FileUploadParser
import os
from django.http import FileResponse

class AudioViewSet(viewsets.ModelViewSet):
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer

    def create(self, request):
        request.data['audio'].name = 'done.mp3'
        serializer = AudioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Audio created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        audio = Audio.objects.get(id=pk)
        audio.audio.open()
        return FileResponse(audio.audio, as_attachment=True, filename=audio.audio.name)

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = [FileUploadParser]

    def create(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.password = make_password(serializer.password)
            serializer.save()
            return Response({'message': 'User created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def destroy(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'User deleted successfully'})

    @action(detail=True, methods=['post'], url_name='login')
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=True, methods=['post'], url_name='logout')
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})
    
    @action(detail=True, methods=['post'], url_name='change_password')
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if user.check_password(old_password):
            user.password = make_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully'})

        return Response({'error': 'Wrong password'}, status=status.HTTP_401_UNAUTHORIZED)

class BabbleViewSet(viewsets.ModelViewSet):
    queryset = Babble.objects.all()
    serializer_class = BabbleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def create(self, request):
        request.data['audio'].name = '%Y/%m/%d'
        serializer = BabbleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Babble created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        babble = Babble.objects.get(pk=pk)
        babble.audio.open()
        return FileResponse(babble.audio, as_attachment=True, filename=babble.audio.name)

    def update(self, request, pk=None):
        babble = Babble.objects.get(pk=pk)
        request.data['audio'].name = '%Y/%m/%d'
        serializer = BabbleSerializer(babble, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Babble updated successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        babble = Babble.objects.get(pk=pk)
        babble.delete()
        return Response({'message': 'Babble deleted successfully'})

    @action(detail=True, methods=['get'])
    def list_all(self, request):
        babble = Babble.objects.all()
        serializer = BabbleSerializer(babble, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_name='rebbable', url_path='rebbable')
    def create_rebabble(self, request):
        serializer = ReBabbleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Rebabble created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def create(self, request):
        request.data['audio'].name = '%Y/%m/%d'
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Comment created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        request.data['audio'].name = '%Y/%m/%d'
        serializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Comment updated successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response({'message': 'Comment deleted successfully'})

    def list(self, request):
        user = request.user
        babble = Babble.objects.get(user=user)
        comments = Comment.objects.filter(babble=babble)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        comment.audio.open()
        return FileResponse(comment.audio, as_attachment=True, filename=comment.audio.name) 

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def create(self, request):
        serializer = FollowerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Follower created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        follower = Follower.objects.get(pk=pk)
        follower.delete()
        return Response({'message': 'Follower deleted successfully'})

    @action(detail=True, methods=['get'])
    def get_followings(self, request):
        user = request.user
        follower = Follower.objects.filter(user=user)
        serializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_followers(self, request):
        user = request.user
        follower = Follower.objects.filter(following=user)
        serializer = FollowerSerializer(follower, many=True)
        return Response(serializer.data)

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def create(self, request):
        serializer = LikeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Like created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        like = Like.objects.get(pk=pk)
        like.delete()
        return Response({'message': 'Like deleted successfully'})

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def create(self, request):
        serializer = TagSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Tag created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        tag = Tag.objects.get(pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    def update(self, request, pk=None):
        tag = Tag.objects.get(pk=pk)
        serializer = TagSerializer(tag, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Tag updated successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        tag = Tag.objects.get(pk=pk)
        tag.delete()
        return Response({'message': 'Tag deleted successfully'})

    def list(self, request):
        user = request.user
        tags = Tag.objects.filter(user=user)
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


# Path: python-django-audio-twitter\audiotwitter\audiotwitter\urls.py