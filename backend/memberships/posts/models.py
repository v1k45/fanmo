import metadata_parser
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.core.cache import cache
from mptt.models import MPTTModel, TreeForeignKey, MPTTModelBase
from micawber.providers import bootstrap_oembed
from micawber.exceptions import ProviderException
from versatileimagefield.fields import VersatileImageField


from memberships.subscriptions.models import Membership, Subscription, Tier
from memberships.utils.models import BaseModel, BaseModelMeta


def annotate_post_permissions(object_list, fan_user):
    """
    Annotate `can_access` and `can_comment` attributes to post objects based on the fan user.
    """

    posts = []
    for post in object_list:
        membership = (
            fan_user.get_membership(post.author_user_id)
            if fan_user.is_authenticated
            else None
        )
        # post authors can access and comment
        if post.author_user_id == fan_user.pk:
            can_access = True
            can_comment = True
        # public posts can be seen by anyone, but commented by members
        elif post.visibility == Post.Visiblity.PUBLIC:
            can_access = True
            can_comment = membership is not None
        # member posts can be seen by members, and commented by members
        elif post.visibility == Post.Visiblity.ALL_MEMBERS:
            can_access = membership is not None
            can_comment = can_access
        # select member posts can be seen select members, and commented by select members
        elif post.visibility == Post.Visiblity.ALLOWED_TIERS:
            can_access = membership is not None and any(
                (tier.id == membership.tier_id for tier in post.allowed_tiers.all())
            )
            can_comment = can_access
        else:
            can_access = False
            can_comment = False

        post.can_access = can_access
        post.can_comment = can_comment

        posts.append(post)

    return posts


class Post(BaseModel):
    class Visiblity(models.TextChoices):
        PUBLIC = "public"
        ALL_MEMBERS = "all_members"
        ALLOWED_TIERS = "allowed_tiers"

    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="title", allow_duplicates=True)
    content = models.OneToOneField("posts.Content", on_delete=models.CASCADE)

    author_user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    visibility = models.CharField(
        max_length=16, choices=Visiblity.choices, default=Visiblity.PUBLIC
    )
    allowed_tiers = models.ManyToManyField("subscriptions.Tier")

    is_published = models.BooleanField(default=True)

    def annotate_permissions(self, fan_user):
        annotate_post_permissions([self], fan_user)


class Content(BaseModel):
    class Type(models.TextChoices):
        TEXT = "text"
        IMAGE = "image"
        IMAGES = "images"
        ATTACHMENTS = "attachments"
        LINK = "link"

    type = models.CharField(max_length=16, choices=Type.choices)
    text = models.TextField(blank=True)
    image = VersatileImageField(upload_to="uploads/content/", blank=True)
    link = models.URLField(blank=True)

    # todo: single link_metadata field?
    link_og = models.JSONField(default=None, null=True, blank=True)
    link_embed = models.JSONField(blank=True, null=True, default=None)

    def update_link_metadata(self, commit=True):
        if self.type != self.Type.LINK:
            return

        try:
            oembed_providers = bootstrap_oembed(cache)
            self.link_embed = oembed_providers.request(self.link)
        except ProviderException:
            pass

        try:
            self.link_og = {"og": None, "page": None, "meta": None}
            metadata = metadata_parser.MetadataParser(
                url=self.link, support_malformed=True, search_head_only=False
            ).metadata
            if metadata.get("og"):
                self.link_og["og"] = metadata["og"]
            if metadata.get("page"):
                self.link_og["page"] = metadata["page"]
            if metadata.get("meta"):
                self.link_og["meta"] = {
                    key.lower(): value for key, value in metadata["meta"].items()
                }
        except metadata_parser.NotParsable:
            pass

        if commit:
            self.save()


class ContentFile(BaseModel):
    class Type(models.TextChoices):
        IMAGE = "image"
        ATTACHMENT = "attachment"

    type = models.CharField(max_length=16, choices=Type.choices, default=Type.IMAGE)
    content = models.ForeignKey(
        "posts.Content", on_delete=models.CASCADE, related_name="files"
    )
    image = VersatileImageField(upload_to="uploads/content/", blank=True)
    attachment = models.FileField(upload_to="uploads/content/", blank=True)

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class CommentModelMeta(type(BaseModel), type(MPTTModel)):
    pass


class Comment(BaseModel, MPTTModel, metaclass=CommentModelMeta):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    body = models.TextField()
    author_user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["created_at"]


class Reaction(BaseModel):
    class Emoji(models.TextChoices):
        HEART = "heart"

    emoji = models.CharField(max_length=16, choices=Emoji.choices)
    post = models.ForeignKey(
        "posts.Post", on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        "posts.Comment", on_delete=models.CASCADE, null=True, blank=True
    )
    author_user = models.ForeignKey("users.User", on_delete=models.CASCADE)
