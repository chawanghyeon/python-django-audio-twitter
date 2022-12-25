from rest_framework.serializers import ModelSerializer, StringRelatedField
from .models import Babble, Comment, Follower, Like, ReBabble, Tag, User

class CommentSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        model = Comment
        fields = '__all__'
        depth = 1
        exclude = ('babble')

class FollowerSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    following = StringRelatedField(many=False)
    class Meta:
        model = Follower
        fields = '__all__'

class LikeSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        model = Like
        fields = '__all__'
        exclude = ('babble')

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class BabbleSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        model = Babble
        fields = '__all__'
        depth = 1

class ReBabbleSerializer(ModelSerializer):
    user = StringRelatedField(many=False)
    class Meta:
        model = ReBabble
        fields = '__all__'
        depth = 1

class UserSerializer(ModelSerializer):
    babbles = BabbleSerializer(many=True, read_only=True)
    reBabbles = ReBabbleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        depth = 1
        exclude = ('password')