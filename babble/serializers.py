from rest_framework.serializers import CharField, ModelSerializer, StringRelatedField

from .models import *


class UserInSerializer(ModelSerializer):
    class Meta:
        fields: tuple = (
            "id",
            "nickname",
            "first_name",
            "last_name",
            "image",
            "background",
        )
        model: User = User
        depth: int = 1


class CommentSerializer(ModelSerializer):
    user: UserInSerializer = UserInSerializer(many=False)

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


class BabbleSerializer(ModelSerializer):
    user: UserInSerializer = UserInSerializer(many=False, read_only=True)
    tags: StringRelatedField = StringRelatedField(many=True)
    is_liked: bool = False
    is_rebabbled: bool = False

    class Meta:
        fields: str = "__all__"
        model: Babble = Babble
        depth: int = 1


class CacheBabbleSerializer(ModelSerializer):
    is_liked: bool = False
    is_rebabbled: bool = False

    class Meta:
        fields: tuple = ("id",)
        model: Babble = Babble
        depth: int = 1


class LikeBabbleSerializer(ModelSerializer):
    babbles: BabbleSerializer = BabbleSerializer(many=True)

    class Meta:
        fields: str = "babble"
        model: Like = Like
        depth: int = 1
