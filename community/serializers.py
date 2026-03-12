from rest_framework import serializers
from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_username",
            "title",
            "content",
            "related_team",
            "related_player",
            "comment_count",
            "like_count",
            "is_liked_by_me",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "author",
            "author_username",
            "comment_count",
            "like_count",
            "is_liked_by_me",
            "created_at",
            "updated_at",
        ]
    
    def get_is_liked_by_me(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.liked_by.filter(id=request.user.id).exists()


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "author_username",
            "content",
            "like_count",
            "is_liked_by_me",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "author",
            "author_username",
            "like_count",
            "is_liked_by_me",
            "created_at",
            "updated_at",
        ]
    
    def get_is_liked_by_me(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.liked_by.filter(id=request.user.id).exists()