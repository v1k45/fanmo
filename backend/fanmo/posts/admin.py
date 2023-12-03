# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Comment, Content, ContentFile, Post, Reaction, Section


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
        "is_published",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "content",
        "author_user",
        "allowed_tiers",
        "is_published",
    )
    search_fields = ("slug",)
    date_hierarchy = "created_at"


class ContentFileInlineAdmin(admin.StackedInline):
    model = ContentFile


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
    inlines = [ContentFileInlineAdmin]


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


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "slug",
        "creator_user",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "creator_user",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    date_hierarchy = "created_at"
