from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    SerializerMethodField,
    StringRelatedField,
)

from project.models import *


class UserInSerializer(ModelSerializer):
    class Meta:
        fields = (
            "pk",
            "nickname",
            "first_name",
            "last_name",
            "image",
            "background",
        )
        model = User
        depth = 1


class CommentSerializer(ModelSerializer):
    user = UserInSerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        depth = 1
        exclude = ("babble",)


class FollowerSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    following = StringRelatedField(many=False)

    class Meta:
        fields = "__all__"
        model = Follower
        depth = 1


class LikeSerializer(ModelSerializer):
    user = StringRelatedField(many=False)

    class Meta:
        fields = "__all__"
        model = Like
        depth = 1


class TagSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Tag
        depth = 1


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        fields = "__all__"
        model = User
        depth = 1


class BabbleSerializer(ModelSerializer):
    user = UserInSerializer(many=False, read_only=True)
    tags = StringRelatedField(many=True)
    is_liked = SerializerMethodField()
    is_rebabbled = SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Babble
        depth = 1

    def get_is_liked(self, obj: Babble) -> bool:
        return False

    def get_is_rebabbled(self, obj: Babble) -> bool:
        return False


class LikeBabbleSerializer(ModelSerializer):
    babbles = BabbleSerializer(many=True)

    class Meta:
        fields = ("babble",)
        model = Like
        depth = 1


class RebabbleSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Rebabble
        depth = 1
