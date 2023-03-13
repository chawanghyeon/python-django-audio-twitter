from rest_framework.serializers import CharField, ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        fields = "__all__"
        model = User
        depth = 1


class UserInSerializer(ModelSerializer):
    class Meta:
        fields = (
            "id",
            "nickname",
            "first_name",
            "last_name",
            "image",
            "background",
        )
        model = User
        depth = 1
