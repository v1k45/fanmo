# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Comment, Content, Post, Reaction


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "title",
        "slug",
        "content",
        "author_user",
        "visibility",
        "minimum_tier",
        "is_published",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "content",
        "author_user",
        "minimum_tier",
        "is_published",
    )
    search_fields = ("slug",)
    date_hierarchy = "created_at"


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "type",
        "text",
        "image",
        "link",
        "link_og",
        "link_embed",
    )
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "post",
        "body",
        "author_user",
        "is_published",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "post",
        "author_user",
        "is_published",
    )
    date_hierarchy = "created_at"


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "emoji",
        "post",
        "author_user",
    )
    list_filter = ("created_at", "updated_at", "post", "author_user")
    date_hierarchy = "created_at"