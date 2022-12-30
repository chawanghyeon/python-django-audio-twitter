from rest_framework.serializers import ModelSerializer, StringRelatedField, ImageField, FileField
from .models import *

class CommentSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        model = Comment
        depth = 1
        exclude = ('babble',)

class FollowerSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    following = StringRelatedField(many=False)
    class Meta:
        model = Follower

class LikeSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        model = Like
        exclude = ('babble',)

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag

class BabbleSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        model = Babble
        depth = 1

class UserSerializer(ModelSerializer):
    babbles = BabbleSerializer(many=True, read_only=True)
    image = ImageField(use_url=True)

    class Meta:
        model = User
        depth = 1
        exclude = ('password',)
