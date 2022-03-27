import metadata_parser
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.core.cache import cache
from micawber.providers import bootstrap_oembed
from micawber.exceptions import ProviderException
from versatileimagefield.fields import VersatileImageField

from memberships.subscriptions.models import Membership, Subscription, Tier
from memberships.utils.models import BaseModel


class PostQuerySet(models.QuerySet):
    def with_permissions(self, fan_user):
        fan_user_id = fan_user.pk
        qs = (
            # Find the active membership between post author and fan
            self.annotate(
                membership_tier=models.FilteredRelation(
                    "author_user__members__tier",
                    condition=models.Q(
                        author_user__members__fan_user_id=fan_user_id,
                        author_user__members__is_active=True,
                    ),
                )
            )
            # Extract membership tier amount
            .annotate(tier_amount=models.F("membership_tier__amount"))
            # Determine access
            .annotate(
                can_access=models.Case(
                    # Author can always access their own posts.
                    models.When(author_user_id=fan_user_id, then=True),
                    # Everyone can access public posts.
                    models.When(visibility=self.model.Visiblity.PUBLIC, then=True),
                    # Everyone can access public posts.
                    models.When(visibility=self.model.Visiblity.PUBLIC, then=True),
                    # Only members can access "all member" content.
                    models.When(
                        visibility=self.model.Visiblity.ALL_MEMBERS,
                        membership_tier__isnull=False,
                        then=True,
                    ),
                    # Only members can members with certian tier can access "allowed tiers" content.
                    models.When(
                        visibility=self.model.Visiblity.ALLOWED_TIERS,
                        allowed_tiers=models.F("membership_tier"),
                        then=True,
                    ),
                    default=False,
                    output_field=models.BooleanField(),
                ),
                can_comment=models.Case(
                    models.When(author_user_id=fan_user_id, then=True),
                    # ony members can interact with a post, even if the post is public
                    models.When(
                        visibility=self.model.Visiblity.PUBLIC,
                        tier_amount__isnull=False,
                        then=True,
                    ),
                    models.When(
                        can_access=True,
                        visibility__in=[
                            self.model.Visiblity.ALL_MEMBERS,
                            self.model.Visiblity.ALLOWED_TIERS,
                        ],
                        then=True,
                    ),
                    default=False,
                    output_field=models.BooleanField(),
                ),
            )
        )
        return qs


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

    objects = PostQuerySet.as_manager()


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
            oembed_providers = bootstrap_oembed(cache)
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
