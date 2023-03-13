from rest_framework.serializers import ModelSerializer

from rebabbles.models import Rebabble


class RebabbleSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Rebabble
        depth = 1
