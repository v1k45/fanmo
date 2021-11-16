from functools import lru_cache
from rest_framework import serializers

from memberships.posts.models import Content, Post
from memberships.users.api.serializers import UserPreviewSerializer


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ["type", "text", "image", "link", "link_og", "link_embed"]
        read_only_fields = ["link_og", "link_embed"]


class PostSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    author_user = UserPreviewSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "visibility",
            "minimum_tier",
            "author_user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author_user", "slug"]

    def get_content(self, post):
        user = self.context["request"].user
        if post.is_locked(user):
            return None
        return ContentSerializer(post.content).data


class PostCreateSerializer(PostSerializer):
    content = ContentSerializer()

    class Meta(PostSerializer.Meta):
        pass

    def create(self, validated_data):
        validated_data["content"] = Content.objects.create(**validated_data["content"])
        validated_data["author_user"] = self.context["request"].user
        return super().create(validated_data)
