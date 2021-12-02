from django.db import models
from micawber.exceptions import ProviderException
from versatileimagefield.fields import VersatileImageField

from memberships.utils.models import BaseModel
from memberships.subscriptions.models import Subscription
from django_extensions.db.fields import AutoSlugField
from memberships.posts.integrations import oembed_providers
import metadata_parser


class Post(BaseModel):
    class Visiblity(models.TextChoices):
        PUBLIC = "public"
        ALL_MEMBERS = "all_members"
        MINIMUM_TIER = "minimum_tier"

    title = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="title", allow_duplicates=True)
    content = models.OneToOneField("posts.Content", on_delete=models.CASCADE)

    author_user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    visibility = models.CharField(
        max_length=16, choices=Visiblity.choices, default=Visiblity.PUBLIC
    )
    minimum_tier = models.ForeignKey(
        "subscriptions.Tier", on_delete=models.SET_NULL, null=True
    )

    is_published = models.BooleanField(default=True)

    # lru cache?
    def is_locked(self, user):
        # author gets to see their own posts
        if user.pk == self.author_user_id:
            return False

        # anyone can see public posts
        if self.visibility == Post.Visiblity.PUBLIC:
            return False

        if user.is_anonymous:
            return True

        # todo cache
        try:
            active_subscription = Subscription.objects.active(self.author_user, user)
        except Subscription.DoesNotExist:
            return False

        if self.visibility == Post.Visiblity.ALL_MEMBERS:
            return True

        return active_subscription.plan.amount >= self.minimum_tier.amount


class Content(BaseModel):
    class Type(models.TextChoices):
        TEXT = "text"
        IMAGE = "image"
        LINK = "link"

    type = models.CharField(max_length=16, choices=Type.choices)
    text = models.TextField(blank=True)
    image = VersatileImageField(upload_to="uploads/content/", blank=True)
    link = models.URLField(blank=True)

    # todo: single link_metadata field?
    link_og = models.JSONField(default=None, null=True, blank=True)
    link_embed = models.JSONField(blank=True, null=True, default=None)

    def update_link_metadata(self):
        if self.type != self.Type.LINK:
            return

        try:
            self.link_embed = oembed_providers.request(self.link)
        except ProviderException:
            pass

        try:
            self.link_og = {"og": None, "page": None}
            metadata = metadata_parser.MetadataParser(
                url=self.link, support_malformed=True, search_head_only=False
            ).metadata
            if metadata.get("og"):
                self.link_og["og"] = metadata["og"]
            if metadata.get("page"):
                self.link_og["page"] = metadata["page"]
        except metadata_parser.NotParsable:
            pass

        self.save()


class Comment(BaseModel):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    body = models.TextField()
    author_user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    is_published = models.BooleanField(default=True)


class Reaction(BaseModel):
    class Emoji(models.TextChoices):
        HEART = "heart"

    emoji = models.CharField(max_length=16, choices=Emoji.choices)
    # support comments in future?
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    author_user = models.ForeignKey("users.User", on_delete=models.CASCADE)
