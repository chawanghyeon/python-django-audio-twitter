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
        fields: str = "__all__"
        model: Like = Like
        depth: int = 1


class TagSerializer(ModelSerializer):
    class Meta:
        fields: str = "__all__"
        model: Tag = Tag
        depth: int = 1


class UserSerializer(ModelSerializer):
    password: CharField = CharField(write_only=True)

    class Meta:
        fields: str = "__all__"
        model: User = User
        depth: int = 1


class UserInBabbleSerializer(ModelSerializer):
    class Meta:
        fields: str = (
            "id",
            "first_name",
            "last_name",
            "image",
            "nickname",
            "background",
        )
        model: User = User
        depth: int = 1


class BabbleSerializer(ModelSerializer):
    user: UserInBabbleSerializer = UserInBabbleSerializer(many=False, read_only=True)
    tags: StringRelatedField = StringRelatedField(many=True)

    class Meta:
        fields: str = "__all__"
        model: Babble = Babble
        depth: int = 1
