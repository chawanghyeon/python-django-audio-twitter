from rest_framework.serializers import CharField, ModelSerializer, StringRelatedField

from .models import *


class CommentSerializer(ModelSerializer):
    user: StringRelatedField = StringRelatedField(many=False)

    class Meta:
        model: Comment = Comment
        depth: int = 1
        exclude: tuple = ("babble",)


class FollowerSerializer(ModelSerializer):
    user: StringRelatedField = StringRelatedField(many=False)
    following: StringRelatedField = StringRelatedField(many=False)

    class Meta:
        fields: str = "__all__"
        model: Follower = Follower
        depth: int = 1


class LikeSerializer(ModelSerializer):
    user: StringRelatedField = StringRelatedField(many=False)

    class Meta:
        model: Like = Like
        exclude: tuple = ("babble",)
        depth: int = 1


class TagSerializer(ModelSerializer):
    class Meta:
        fields: str = "__all__"
        model: Tag = Tag
        depth: int = 1


class BabbleSerializer(ModelSerializer):
    user: StringRelatedField = StringRelatedField(many=False)

    class Meta:
        fields: str = "__all__"
        model: Babble = Babble
        depth: int = 1


class UserSerializer(ModelSerializer):
    babbles: BabbleSerializer = BabbleSerializer(
        many=True, read_only=True, required=False
    )
    password: CharField = CharField(write_only=True, required=False)

    class Meta:
        fields: str = "__all__"
        model: User = User
        depth: int = 1
