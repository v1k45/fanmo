from django.db import models
from versatileimagefield.fields import VersatileImageField

from memberships.utils.models import BaseModel
from django_extensions.db.fields import AutoSlugField


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


class Content(BaseModel):
    class Type(models.TextChoices):
        TEXT = "text"
        IMAGE = "image"
        LINK = "link"

    type = models.CharField(max_length=16, choices=Type.choices)
    text = models.TextField(blank=True)
    image = VersatileImageField(upload_to="uploads/content/")
    link = models.URLField()
    link_og = models.JSONField()
    link_embed = models.JSONField()


class Comment(BaseModel):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)
    body = models.TextField()
    author_user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    is_published = models.BooleanField(default=True)
