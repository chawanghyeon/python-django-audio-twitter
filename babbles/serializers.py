from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    StringRelatedField,
)

from babbles.models import Babble
from users.serializers import UserInSerializer


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
