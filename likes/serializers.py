from rest_framework.serializers import ModelSerializer, StringRelatedField

from likes.models import Like


class LikeSerializer(ModelSerializer):
    user = StringRelatedField(many=False)

    class Meta:
        fields = "__all__"
        model = Like
        depth = 1
