from rest_framework import serializers
from accounts.models import User
from .models import Post, Comment, Like, Save, Share


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']


class CreateCommentSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1, max_length=2000)


class PostSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()
    saves_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_shared = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'image', 'created_at', 'updated_at',
            'comments', 'likes_count', 'comments_count', 'shares_count', 'saves_count',
            'is_liked', 'is_saved', 'is_shared'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.filter(deleted_at__isnull=True).count()

    def get_shares_count(self, obj):
        return obj.shares.count()

    def get_saves_count(self, obj):
        return obj.saves.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.saves.filter(user=request.user).exists()

    def get_is_shared(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.shares.filter(user=request.user).exists()


class CreatePostSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1, max_length=5000)
    image = serializers.URLField(required=False, allow_blank=True)
