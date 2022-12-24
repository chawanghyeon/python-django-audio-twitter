from .serializer import BabbleSerializer, CommentSerializer, FollowerSerializer, LikeSerializer, ReBabbleSerializer, TagSerializer, UserSerializer
from .models import Babble, Comment, Follower, Like, ReBabble, Tag, User
from rest_framework import viewsets

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class BabbleViewSet(viewsets.ModelViewSet):
    queryset = Babble.objects.all()
    serializer_class = BabbleSerializer

class ReBabbleViewSet(viewsets.ModelViewSet):
    queryset = ReBabble.objects.all()
    serializer_class = ReBabbleSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

# Path: python-django-audio-twitter\audiotwitter\audiotwitter\urls.py