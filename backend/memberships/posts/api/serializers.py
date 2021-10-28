from rest_framework import serializers

from memberships.posts.models import Content, Post


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ["type", "text", "image", "link", "link_og", "link_embed"]


class PostSerializer(serializers.ModelSerializer):
    content = ContentSerializer()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "visibility",
            "minimum_tier",
            "is_published",
            "created_at",
            "updated_at",
        ]
