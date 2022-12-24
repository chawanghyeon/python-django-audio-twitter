from rest_framework.serializers import ModelSerializer
from .models import Babble, Comment, Follower, Like, ReBabble, Tag, User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        depth = 1

class CommentSerializer(ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'
        depth = 1

class FollowerSerializer(ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'

class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class BabbleSerializer(ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Babble
        fields = '__all__'
        depth = 1

class ReBabbleSerializer(ModelSerializer):
    babble = BabbleSerializer(many=False, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = ReBabble
        fields = '__all__'
        depth = 1