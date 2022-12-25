from .serializers import BabbleSerializer, CommentSerializer, FollowerSerializer, LikeSerializer, ReBabbleSerializer, TagSerializer, UserSerializer
from .models import Babble, Comment, Follower, Like, ReBabble, Tag, User
from rest_framework import viewsets
from rest_framework.response import Response, status
from rest_framework.decorators import action
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_name='signup')
    def signup(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

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
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        user = request.user
        user.delete()
        return Response({'message': 'User deleted successfully'})

    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def update(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)



class BabbleViewSet(viewsets.ModelViewSet):
    queryset = Babble.objects.all()
    serializer_class = BabbleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def create(self, request):
        serializer = BabbleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Babble created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk=None):
        babble = Babble.objects.get(pk=pk)
        serializer = BabbleSerializer(babble)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def update(self, request, pk=None):
        babble = Babble.objects.get(pk=pk)
        serializer = BabbleSerializer(babble, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Babble updated successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        babble = Babble.objects.get(pk=pk)
        babble.delete()
        return Response({'message': 'Babble deleted successfully'})
    
    @action(detail=True, methods=['get'])
    def list(self, request):
        user = request.user
        babble = Babble.objects.filter(user=user)
        serializer = BabbleSerializer(babble, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_all(self, request):
        babble = Babble.objects.all()
        serializer = BabbleSerializer(babble, many=True)
        return Response(serializer.data)


class ReBabbleViewSet(viewsets.ModelViewSet):
    queryset = ReBabble.objects.all()
    serializer_class = ReBabbleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def create(self, request):
        serializer = ReBabbleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'ReBabble created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk=None):
        rebabble = ReBabble.objects.get(pk=pk)
        serializer = ReBabbleSerializer(rebabble)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def update(self, request, pk=None):
        rebabble = ReBabble.objects.get(pk=pk)
        serializer = ReBabbleSerializer(rebabble, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'ReBabble updated successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        rebabble = ReBabble.objects.get(pk=pk)
        rebabble.delete()
        return Response({'message': 'ReBabble deleted successfully'})

    @action(detail=True, methods=['get'])
    def list(self, request):
        user = request.user
        rebabble = ReBabble.objects.filter(user=user)
        serializer = ReBabbleSerializer(rebabble, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_all(self, request):
        rebabble = ReBabble.objects.all()
        serializer = ReBabbleSerializer(rebabble, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def create(self, request):
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Comment created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def update(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        serializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Comment updated successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response({'message': 'Comment deleted successfully'})

    @action(detail=True, methods=['get'])
    def list(self, request):
        user = request.user
        comment = Comment.objects.filter(user=user)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def list_all(self, request):
        comment = Comment.objects.all()
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data)

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def create(self, request):
        serializer = FollowerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Follower created successfully'})

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
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

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

# Path: python-django-audio-twitter\audiotwitter\audiotwitter\urls.py