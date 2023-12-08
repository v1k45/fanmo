import bleach
from bleach.css_sanitizer import CSSSanitizer
from django.conf import settings
from django.urls import reverse
from djmoney.contrib.django_rest_framework.fields import MoneyField
from drf_extra_fields.fields import Base64FileField, Base64ImageField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from fanmo.donations.models import Donation
from fanmo.memberships.api.serializers import TierPreviewSerializer
from fanmo.memberships.models import Tier
from fanmo.posts.models import (
    Comment,
    Content,
    ContentFile,
    Post,
    PostImage,
    PostMeta,
    Reaction,
    Section,
)
from fanmo.users.api.serializers import PublicUserSerializer, UserPreviewSerializer
from fanmo.utils.fields import FileField, VersatileImageFieldSerializer


class ContentFileSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer("post_image", read_only=True)
    image_base64 = Base64ImageField(write_only=True, required=False, source="image")
    attachment = FileField(read_only=True)
    attachment_base64 = Base64FileField(write_only=True, required=False, source="file")

    class Meta:
        model = ContentFile
        fields = [
            "id",
            "type",
            "image",
            "image_base64",
            "attachment",
            "attachment_base64",
        ]
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

    def validate_text(self, text):
        css_sanitizer = CSSSanitizer(allowed_css_properties=["text-align"])

        return bleach.clean(
            text,
            tags=[
                "p",
                "b",
                "strong",
                "i",
                "u",
                "strike",
                "em",
                "s",
                "br",
                "a",
                "h3",
                "ol",
                "ul",
                "li",
                "blockquote",
                "hr",
                "img",
            ],
            attributes={
                "a": ["href", "rel", "target"],
                "img": ["src"],
                "p": ["style"],
                "h3": ["style"],
            },
            css_sanitizer=css_sanitizer,
        )

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


class SectionPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "name", "slug", "description", "show_in_menu"]


class PostMetaSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer("post_image", read_only=True)
    image_base64 = Base64ImageField(write_only=True, required=False, source="image")

    class Meta:
        model = PostMeta
        fields = ["title", "description", "keywords", "image", "image_base64"]


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


class PostPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "slug"]


class PostSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    author_user = UserPreviewSerializer(read_only=True)
    stats = PostStatsSerializer(source="*", read_only=True)
    meta = PostMetaSerializer()
    can_access = serializers.SerializerMethodField()
    can_comment = serializers.SerializerMethodField()
    minimum_tier = serializers.SerializerMethodField()
    section = SectionPreviewSerializer(read_only=True)
    section_id = serializers.PrimaryKeyRelatedField(
        source="section",
        queryset=Section.objects.all(),
        write_only=True,
        allow_null=True,
        required=False,
    )
    allowed_tiers = TierPreviewSerializer(many=True, read_only=True)
    allowed_tiers_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        allow_empty=True,
        required=False,
        queryset=Tier.objects.filter(is_public=True),
        source="allowed_tiers",
    )
    minimum_amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        default_currency="INR",
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "stats",
            "meta",
            "visibility",
            "section",
            "section_id",
            "allowed_tiers",
            "allowed_tiers_ids",
            "is_purchaseable",
            "minimum_amount",
            "can_access",
            "can_comment",
            "minimum_tier",
            "author_user",
            "is_pinned",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author_user", "slug", "stats", "allowed_tiers"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tiers_qs = self.fields["allowed_tiers_ids"].child_relation.queryset
        self.fields["allowed_tiers_ids"].child_relation.queryset = tiers_qs.filter(
            creator_user=self.context["request"].user.pk
        )
        section_qs = self.fields["section_id"].queryset
        self.fields["section_id"].queryset = section_qs.filter(
            creator_user=self.context["request"].user.pk
        )

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

    @extend_schema_field(TierPreviewSerializer())
    def get_minimum_tier(self, post):
        if minimum_tier := getattr(post, "minimum_tier", None):
            return TierPreviewSerializer(minimum_tier, context=self.context).data


class PostDetailSerializer(PostSerializer):
    author_user = PublicUserSerializer(read_only=True)


class PostUpdateSerializer(PostDetailSerializer):
    content = ContentSerializer()

    class Meta:
        model = Post
        fields = PostSerializer.Meta.fields
        read_only_fields = fields.copy()
        read_only_fields = list(
            set(read_only_fields)
            - set(
                [
                    "is_pinned",
                    "content",
                    "title",
                    "visibility",
                    "section_id",
                    "allowed_tier_ids",
                    "is_purchaseable",
                    "minimum_amount",
                ]
            )
        )

    def validate_is_pinned(self, is_pinned):
        pinned_posts = Post.objects.filter(
            author_user=self.context["request"].user,
            is_published=True,
            is_pinned=True,
        )
        if is_pinned and pinned_posts.count() >= 3:
            raise serializers.ValidationError(
                "You can only have upto 3 pinned posts. Please unpin other posts and try again.",
                "pin_count_exceeded",
            )
        return is_pinned

    def validate(self, attrs):
        if attrs.get("is_purchaseable"):
            if attrs["visibility"] == Post.Visiblity.PUBLIC:
                raise serializers.ValidationError(
                    "Posts with 'public' visibility cannot be purchased.",
                    "not_purchaseable",
                )
            elif (
                attrs["minimum_amount"]
                < self.instance.creator_user.user_preferences.minimum_amount
            ):
                raise serializers.ValidationError(
                    f"Amount cannot be lower than {self.instance.creator_user.user_preferences.minimum_amount} - your minimum tip amount.",
                    "minimum",
                )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        content = validated_data.pop("content", None)
        meta_payload = validated_data.pop("meta", None)
        post = super().update(instance, validated_data)
        if content:
            if "text" in content:
                post.content.text = content["text"]
            if "link" in content and post.content.type == Content.Type.LINK:
                post.content.link = content["link"]
                post.content.update_link_metadata()
            post.content.save()

        if meta_payload:
            if post.meta:
                for attr, value in meta_payload.items():
                    setattr(post.meta, attr, value)
                post.meta.save()
            else:
                post.meta = PostMeta.objects.create(**meta_payload)
                post.save()
        return post


class PostPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "slug", "title"]


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


class CommentReactionSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=["add", "remove"])
    emoji = serializers.ChoiceField(choices=Reaction.Emoji.choices)

    class Meta:
        model = Comment
        fields = ["action", "emoji"]

    def validate(self, attrs):
        user = self.context["request"].user
        if post := self.instance.post:
            post.annotate_permissions(user)
            if not post.can_access:
                raise serializers.ValidationError(
                    "You do not have permission to perform this action",
                    "permission_denied",
                )
        elif donation := self.instance.donation:
            user_id = self.context["request"].user.pk
            if donation.is_hidden and user_id not in [
                donation.creator_user_id,
                donation.fan_user_id,
            ]:
                raise serializers.ValidationError(
                    "You do not have permission to perform this action",
                    "permission_denied",
                )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if validated_data["action"] == "add":
            Reaction.objects.update_or_create(
                comment=instance, author_user=user, emoji=validated_data["emoji"]
            )
        else:
            Reaction.objects.filter(
                comment=instance, author_user=user, emoji=validated_data["emoji"]
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

        meta_payload = validated_data["meta"]
        meta = PostMeta.objects.create(**meta_payload)

        validated_data["content"] = content
        validated_data["author_user"] = self.context["request"].user
        validated_data["meta"] = meta
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.PrimaryKeyRelatedField(
        source="post",
        queryset=Post.objects.filter(is_published=True),
        write_only=True,
        required=False,
    )
    donation_id = serializers.PrimaryKeyRelatedField(
        source="donation",
        queryset=Donation.objects.filter(status=Donation.Status.SUCCESSFUL),
        write_only=True,
        required=False,
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        source="parent",
        queryset=Comment.objects.filter(is_published=True),
        required=False,
        allow_null=True,
        write_only=True,
    )
    body = serializers.CharField(max_length=3000)
    author_user = UserPreviewSerializer(read_only=True)
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post_id",
            "donation_id",
            "parent_id",
            "body",
            "author_user",
            "children",
            "reactions",
            "created_at",
        ]

    def get_fields(self):
        fields = super().get_fields()
        fields["children"] = CommentSerializer(
            many=True, read_only=True, source="get_children"
        )
        return fields

    @extend_schema_field(CommentReactionSerializer(many=True))
    def get_reactions(self, comment):
        reaction_summary = {}
        for reaction in comment.reactions.all():
            reaction_summary.setdefault(
                reaction.emoji,
                {"count": 0, "is_reacted": False, "emoji": reaction.emoji},
            )
            reaction_summary[reaction.emoji]["count"] += 1

            if reaction.author_user_id == self.context["request"].user.pk:
                reaction_summary[reaction.emoji]["is_reacted"] = True

        return reaction_summary.values()

    def validate(self, attrs):
        if not attrs.get("post") and not attrs.get("donation"):
            raise serializers.ValidationError(
                "One of post_id or donation_id is required", "required"
            )
        if attrs.get("post") and attrs.get("donation"):
            raise serializers.ValidationError(
                "Only one of post_id or donation_id are allowed", "multiple_values"
            )

        if attrs.get("parent"):
            if attrs.get("donation"):
                raise serializers.ValidationError(
                    "Comment replies are not allowed in tips."
                )
            elif attrs["parent"].post_id != attrs["post"].id:
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

    def validate_donation_id(self, donation):
        if self.context["request"].user.pk not in [
            donation.creator_user_id,
            donation.fan_user_id,
        ]:
            raise serializers.ValidationError(
                "You don't have permission to comment on this tip.",
                "permission_denied",
            )
        return donation

    def create(self, validated_data):
        validated_data["author_user"] = self.context["request"].user
        return super().create(validated_data)


class CommentPreviewSerializer(serializers.ModelSerializer):
    post = PostPreviewSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "parent_id", "post", "body"]


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


class PostImageProxySerializer(serializers.ModelSerializer):
    small = serializers.SerializerMethodField()
    medium = serializers.SerializerMethodField()
    full = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ["small", "medium", "full"]

    def get_small(self, post_image):
        return self._get_post_image(post_image, "small")

    def get_medium(self, post_image):
        return self._get_post_image(post_image, "medium")

    def get_full(self, post_image):
        return self._get_post_image(post_image, "full")

    def _get_post_image(self, post_image, size):
        return settings.BASE_URL + reverse(
            "post_image_proxy", args=[post_image.uuid, size]
        )


class PostImageSerializer(serializers.ModelSerializer):
    image = PostImageProxySerializer(source="*", read_only=True)
    image_base64 = Base64ImageField(write_only=True, required=True, source="image")

    class Meta:
        model = PostImage
        fields = ["id", "image", "image_base64", "created_at", "updated_at"]


class SectionSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ["id", "name", "slug", "description", "show_in_menu", "post_count", "created_at", "updated_at"]

    @extend_schema_field(serializers.IntegerField())
    def get_post_count(self, section):
        return getattr(section, "post_count", 0)
    
    def validate_name(self, name):
        if self.instance and self.instance.name == name:
            return name

        if Section.objects.filter(creator_user=self.context["request"].user, name__iexact=name).exists():
            raise serializers.ValidationError(
                "You already have a section with this name.", "duplicate_name"
            )
        return name
    
    def validate_description(self, description):
        return bleach.clean(
            description,
            tags=["p", "b", "strong", "i", "u", "strike", "em", "s", "br", "a"],
            attributes={"a": ["href", "rel", "target"]},
        )
