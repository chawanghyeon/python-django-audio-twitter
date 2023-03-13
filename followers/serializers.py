from rest_framework.serializers import ModelSerializer, StringRelatedField

from followers.models import Follower


class FollowerSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    following = StringRelatedField(many=False)

    class Meta:
        fields = "__all__"
        model = Follower
        depth = 1
