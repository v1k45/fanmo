from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from functools import lru_cache
from memberships.core.email import notify_new_post
from mptt.utils import get_cached_trees
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from memberships.posts.api.filters import PostFilter
from django_q.tasks import async_task

from memberships.posts.api.serializers import (
    CommentReactionSerializer,
    CommentSerializer,
    LinkPreviewSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    PostReactionSerializer,
    PostSerializer,
    PostStatsSerializer,
)
from memberships.users.api.permissions import IsCreator
from memberships.posts.models import Comment, Post, annotate_post_permissions


class PostViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet
):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_published=True)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PostFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "destroy":
            queryset = queryset.filter(author_user=self.request.user)

        queryset = (
            queryset.select_related("content", "author_user")
            .prefetch_related(
                "reactions", "allowed_tiers", "content__files", "author_user__tiers"
            )
            .annotate(
                comment_count=Count("comments", filter=Q(comments__is_published=True))
            )
        )
        return queryset.order_by("-created_at")

    def paginate_queryset(self, queryset):
        object_list = super().paginate_queryset(queryset)
        return annotate_post_permissions(object_list, self.request.user)

    def get_object(self):
        post = super().get_object()
        post.annotate_permissions(self.request.user)
        return post

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "reactions":
            return PostReactionSerializer
        if self.action == "link_preview":
            return LinkPreviewSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.is_published = False
        instance.save()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        async_task(notify_new_post, serializer.instance.pk)

    @extend_schema(responses=PostStatsSerializer)
    @action(
        detail=True, permission_classes=[permissions.IsAuthenticated], methods=["POST"]
    )
    def reactions(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=self.request.data, instance=self.get_object()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = PostStatsSerializer(
            self.get_object(), context=self.get_serializer_context()
        )
        return Response(response_serializer.data)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated, IsCreator],
        methods=["POST"],
    )
    def link_preview(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = (
            Comment.objects.filter(is_published=True)
            .select_related("author_user")
            .prefetch_related("reactions")
        )
        if self.action == "list":
            post = self.get_post()
            if post.can_access:
                return queryset.filter(post=post).get_cached_trees()
            else:
                return queryset.none()
        # let comment and post authors delete the comment
        elif self.action == "destroy":
            return queryset.filter(
                Q(author_user=self.request.user)
                | Q(post__author_user=self.request.user)
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "reactions":
            return CommentReactionSerializer
        return super().get_serializer_class()

    @lru_cache
    def get_post(self):
        try:
            post: Post = Post.objects.get(
                is_published=True, id=self.request.query_params.get("post_id")
            )
        except (Post.DoesNotExist, ValueError):
            raise ValidationError("Invalid post_id.")

        post.annotate_permissions(self.request.user)
        return post

    def perform_destroy(self, instance):
        instance.get_descendants(include_self=True).update(is_published=False)

    @extend_schema(responses=CommentSerializer)
    @action(
        detail=True, permission_classes=[permissions.IsAuthenticated], methods=["POST"]
    )
    def reactions(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = self.get_serializer(data=self.request.data, instance=comment)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        comment_trees = get_cached_trees(
            comment.get_descendants(include_self=True).filter(is_published=True)
        )
        response_serializer = CommentSerializer(
            comment_trees[0], context=self.get_serializer_context()
        )
        return Response(response_serializer.data)
