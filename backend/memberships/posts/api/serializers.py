from collections import defaultdict
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from memberships.posts.models import Content, Post, Reaction
from memberships.users.api.serializers import UserPreviewSerializer

from drf_spectacular.utils import extend_schema_field


class ContentSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer("post_image", read_only=True)
    image_base64 = Base64ImageField(write_only=True, required=False, source="image")

    class Meta:
        model = Content
        fields = [
            "type",
            "text",
            "image",
            "image_base64",
            "link",
            "link_og",
            "link_embed",
        ]
        read_only_fields = ["link_og", "link_embed", "image"]


class PostReactionSummarySerializer(serializers.Serializer):
    emoji = serializers.ChoiceField(choices=Reaction.Emoji.choices)
    count = serializers.IntegerField()
    is_reacted = serializers.BooleanField()


class PostSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    author_user = UserPreviewSerializer(read_only=True)
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "reactions",
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
        return ContentSerializer(post.content, context=self.context).data

    @extend_schema_field(PostReactionSummarySerializer(many=True))
    def get_reactions(self, post):
        reaction_summary = {}
        for reaction in post.reactions.all():
            reaction_summary.setdefault(
                reaction.emoji,
                {"count": 0, "is_reacted": False, "emoji": reaction.emoji},
            )
            reaction_summary[reaction.emoji]["count"] += 1

            if reaction.author_user_id == self.context["request"].user.pk:
                reaction_summary[reaction.emoji]["is_reacted"] = True

        return reaction_summary.values()


class PostReactionSerializer(PostSerializer):
    action = serializers.ChoiceField(
        choices=["add", "remove"], default="add", write_only=True
    )
    emoji = serializers.ChoiceField(choices=Reaction.Emoji.choices, write_only=True)

    class Meta:
        model = Post
        fields = ["reactions", "action", "emoji"]
        read_only_fields = ["reactions"]

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if validated_data["action"] == "add":
            Reaction.objects.update_or_create(
                post=instance, author_user=user, emoji=validated_data["emoji"]
            )
        else:
            Reaction.objects.filter(
                post=instance, author_user=user, emoji=validated_data["emoji"]
            ).delete()
        return instance


class PostCreateSerializer(PostSerializer):
    content = ContentSerializer()

    class Meta(PostSerializer.Meta):
        pass

    def create(self, validated_data):
        content = Content.objects.create(**validated_data["content"])
        content.update_link_metadata()

        validated_data["content"] = content
        validated_data["author_user"] = self.context["request"].user
        return super().create(validated_data)
