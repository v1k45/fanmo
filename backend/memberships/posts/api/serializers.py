from collections import defaultdict

from drf_extra_fields.fields import Base64ImageField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from memberships.posts.models import Comment, Content, Post, Reaction
from memberships.users.api.serializers import UserPreviewSerializer
from memberships.utils.fields import VersatileImageFieldSerializer


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
    can_access = serializers.SerializerMethodField()
    can_comment = serializers.SerializerMethodField()

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
            "can_access",
            "can_comment",
            "author_user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author_user", "slug"]

    def get_content(self, post):
        if post.can_access:
            return ContentSerializer(post.content, context=self.context).data

    def get_can_access(self, post):
        return post.can_access

    def get_can_comment(self, post):
        return post.can_comment

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


class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.PrimaryKeyRelatedField(
        source="post", queryset=Post.objects.all(), write_only=True
    )
    author_user = UserPreviewSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post_id", "body", "author_user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["post_id"].queryset = Post.objects.filter(
            is_published=True
        ).with_permissions(self.context["request"].user)

    def validate_post(self, post):
        if not post.can_comment:
            raise serializers.ValidationError("Only members can comment on this post.")
        return post

    def create(self, validated_data):
        validated_data["author_user"] = self.context["request"].user
        return super().create(validated_data)
