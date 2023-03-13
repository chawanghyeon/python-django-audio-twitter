from rest_framework.serializers import ModelSerializer

from comments.models import Comment
from users.serializers import UserInSerializer


class CommentSerializer(ModelSerializer):
    user = UserInSerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        depth = 1
        exclude = ("babble",)
