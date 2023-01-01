from rest_framework.serializers import ModelSerializer, StringRelatedField, CharField
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
        fields = '__all__'
        model = Follower
        depth = 1

class LikeSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        model = Like
        exclude = ('babble',)
        depth = 1

class TagSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag
        depth = 1
class BabbleSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        fields = '__all__'
        model = Babble
        depth = 1

class UserSerializer(ModelSerializer):
    babbles = BabbleSerializer(many=True, read_only=True)
    password = CharField(write_only=True)

    class Meta:
        fields = '__all__'
        model = User
        depth = 1
