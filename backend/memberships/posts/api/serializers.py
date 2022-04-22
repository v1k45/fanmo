from drf_extra_fields.fields import Base64ImageField, Base64FileField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from memberships.posts.models import (
    Comment,
    Content,
    ContentFile,
    Post,
    Reaction,
)
from memberships.users.api.serializers import (
    PublicUserSerializer,
    UserPreviewSerializer,
)
from memberships.utils.fields import VersatileImageFieldSerializer, FileField


class ContentFileSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer("post_image", read_only=True)
    image_base64 = Base64ImageField(write_only=True, required=False, source="image")
    attachment = FileField(read_only=True)
    attachment_base64 = Base64FileField(write_only=True, required=False, source="file")

    class Meta:
        model = ContentFile
        fields = ["type", "image", "image_base64", "attachment", "attachment_base64"]
        read_only_files = ["image", "attachment"]

    def validate(self, attrs):
        if attrs["type"] == ContentFile.Type.IMAGE and "image" not in attrs:
            raise serializers.ValidationError(
                "Image field is required.", "invalid_file"
            )
        if attrs["type"] == ContentFile.Type.ATTACHMENT and "attachment" not in attrs:
            raise serializers.ValidationError(
                "Attachment field is required.", "invalid_file"
            )
        if "image" in attrs and "attachment" in attrs:
            raise serializers.ValidationError(
                "Only one of image or attachment can be submitted.", "invalid_file"
            )
        return super().validate(attrs)


class ContentSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer("post_image", read_only=True)
    image_base64 = Base64ImageField(write_only=True, required=False, source="image")
    files = ContentFileSerializer(many=True, required=False)

    class Meta:
        model = Content
        fields = [
            "type",
            "text",
            "files",
            "image",
            "image_base64",
            "link",
            "link_og",
            "link_embed",
        ]
        read_only_fields = ["link_og", "link_embed", "image"]

    def validate(self, attrs):
        """
        Validate content type with its actual content.
        """
        type = attrs["type"]
        if type == Content.Type.TEXT and not attrs.get("text"):
            raise serializers.ValidationError(
                {"text": serializers.ErrorDetail("This field is required", "required")}
            )

        if type == Content.Type.LINK and not attrs.get("link"):
            raise serializers.ValidationError(
                {"link": serializers.ErrorDetail("This field is required", "required")}
            )

        if type == Content.Type.IMAGES:
            if not attrs.get("files"):
                raise serializers.ValidationError(
                    {
                        "files": serializers.ErrorDetail(
                            "This field is required", "required"
                        )
                    }
                )

            all_files_are_images = all(
                (
                    content_file["type"] == ContentFile.Type.IMAGE
                    for content_file in attrs["files"]
                )
            )
            if not all_files_are_images:
                raise serializers.ValidationError(
                    {
                        "files": serializers.ErrorDetail(
                            "All files must be images", "invalid_files"
                        )
                    }
                )

        if type == Content.Type.ATTACHMENTS:
            if not attrs.get("files"):
                raise serializers.ValidationError(
                    {
                        "files": serializers.ErrorDetail(
                            "This field is required", "required"
                        )
                    }
                )

            all_files_are_attachments = all(
                (
                    content_file["type"] == ContentFile.Type.ATTACHMENT
                    for content_file in attrs["files"]
                )
            )
            if not all_files_are_attachments:
                raise serializers.ValidationError(
                    {
                        "files": serializers.ErrorDetail(
                            "All files must be attachments", "invalid_file"
                        )
                    }
                )

        return super().validate(attrs)


class PostReactionSummarySerializer(serializers.Serializer):
    emoji = serializers.ChoiceField(choices=Reaction.Emoji.choices)
    count = serializers.IntegerField()
    is_reacted = serializers.BooleanField()


class PostStatsSerializer(serializers.ModelSerializer):
    reactions = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["reactions", "comment_count"]

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

    @extend_schema_field(serializers.IntegerField())
    def get_comment_count(self, post):
        return getattr(post, "comment_count", 0)


class PostSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    author_user = UserPreviewSerializer(read_only=True)
    stats = PostStatsSerializer(source="*", read_only=True)
    can_access = serializers.SerializerMethodField()
    can_comment = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "stats",
            "visibility",
            "allowed_tiers",
            "can_access",
            "can_comment",
            "author_user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author_user", "slug", "stats"]
        extra_kwargs = {
            "allowed_tiers": {
                "allow_empty": True,
                "required": False,
            }
        }

    @property
    def is_create_action(self):
        return self.context["view"].action == "create"

    @extend_schema_field(ContentSerializer())
    def get_content(self, post):
        if self.is_create_action or post.can_access:
            return ContentSerializer(post.content, context=self.context).data

    @extend_schema_field(serializers.BooleanField())
    def get_can_access(self, post):
        return self.is_create_action or post.can_access

    @extend_schema_field(serializers.BooleanField())
    def get_can_comment(self, post):
        return self.is_create_action or post.can_comment


class PostDetailSerializer(PostSerializer):
    author_user = PublicUserSerializer(read_only=True)


class PostReactionSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=["add", "remove"])
    emoji = serializers.ChoiceField(choices=Reaction.Emoji.choices)

    class Meta:
        model = Post
        fields = ["action", "emoji"]

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
        content_payload = validated_data["content"]
        files_payload = content_payload.pop("files", [])

        content: Content = Content.objects.create(**content_payload)
        content.update_link_metadata()

        # create each file separately so that the created_at time is consistent
        for idx, file_payload in enumerate(files_payload):
            ContentFile.objects.create(content=content, order=idx, **file_payload)

        validated_data["content"] = content
        validated_data["author_user"] = self.context["request"].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.PrimaryKeyRelatedField(
        source="post", queryset=Post.objects.filter(is_published=True), write_only=True
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        source="parent",
        queryset=Comment.objects.filter(is_published=True),
        required=False,
        allow_null=True,
        write_only=True,
    )
    author_user = UserPreviewSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "post_id",
            "parent_id",
            "body",
            "author_user",
            "children",
            "created_at",
        ]

    def get_fields(self):
        fields = super().get_fields()
        fields["children"] = CommentSerializer(
            many=True, read_only=True, source="get_children"
        )
        return fields

    def validate(self, attrs):
        if attrs.get("parent") and attrs["parent"].post_id != attrs["post"].id:
            raise serializers.ValidationError(
                "Parent comment does not exists in the post."
            )
        return attrs

    def validate_post_id(self, post):
        post.annotate_permissions(self.context["request"].user)
        if not post.can_comment:
            raise serializers.ValidationError(
                "Only members can comment on this post.", "permission_denied"
            )
        return post

    def create(self, validated_data):
        validated_data["author_user"] = self.context["request"].user
        return super().create(validated_data)


class LinkPreviewSerializer(serializers.Serializer):
    link = serializers.URLField()
    link_embed = serializers.JSONField(write_only=True, required=False)
    link_og = serializers.JSONField(write_only=True, required=False)

    def validate(self, attrs):
        content = Content(type=Content.Type.LINK, link=attrs["link"])
        content.update_link_metadata(commit=False)
        attrs["link_og"] = content.link_og
        attrs["link_embed"] = content.link_embed
        return attrs
