from rest_framework.serializers import ModelSerializer, primaryKeyRelatedField
from mvc.models import Babble, Comment, Follower, Like, ReBabble, Tag, User

class UserSerializer(ModelSerializer):
    babbles = primaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "created", "modified", "avatar", "background", "nickname", "location", "phoneNumber", "gender", "bio", "birthday")

class BabbleSerializer(ModelSerializer):
    class Meta:
        model = Babble
        fields = ("id", "user", "fileUrl", "created", "modified")

class ReBabbleSerializer(ModelSerializer):
    class Meta:
        model = ReBabble
        fields = ("id", "babble", "user", "created", "modified")

class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "babble", "fileUrl", "created", "modified")

class FollowerSerializer(ModelSerializer):
    class Meta:
        model = Follower
        fields = ("id", "user", "follower", "created")

class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "babble", "created")

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "babble", "tag", "created")