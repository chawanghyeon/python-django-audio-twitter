from rest_framework.serializers import ModelSerializer

from tags.models import Tag


class TagSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Tag
        depth = 1
