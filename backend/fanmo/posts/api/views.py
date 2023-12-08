from functools import lru_cache

from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from mptt.utils import get_cached_trees
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from fanmo.core.notifications import notify_comment, notify_new_post
from fanmo.core.tasks import async_task
from fanmo.donations.models import Donation
from fanmo.posts.api.filters import PostFilter, SectionFilter
from fanmo.posts.api.serializers import (
    CommentReactionSerializer,
    CommentSerializer,
    LinkPreviewSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    PostImageSerializer,
    PostReactionSerializer,
    PostSerializer,
    PostStatsSerializer,
    PostUpdateSerializer,
    SectionSerializer,
)
from fanmo.posts.models import Comment, Post, Section, annotate_post_permissions
from fanmo.posts.tasks import refresh_post_social_image
from fanmo.users.api.permissions import IsCreator, IsCreatorOrReadOnly
from fanmo.utils.throttling import Throttle


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_published=True)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = PostFilter
    throttle_classes = [Throttle("post_hour", "create")]
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["destroy", "update", "partial_update"]:
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
        if self.action in ["update", "partial_update"]:
            return PostUpdateSerializer
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
        async_task(refresh_post_social_image, serializer.instance.pk)
        async_task(notify_new_post, serializer.instance.pk)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        async_task(refresh_post_social_image, serializer.instance.pk)

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
    throttle_classes = [Throttle("comment_hour", "create")]

    def get_queryset(self):
        queryset = (
            Comment.objects.filter(is_published=True)
            .select_related("author_user")
            .prefetch_related("reactions")
        )
        if self.action == "list":
            if "post_id" in self.request.query_params:
                post = self.get_post()
                if post.can_access:
                    return queryset.filter(post=post).get_cached_trees()
                else:
                    return queryset.none()
            elif "donation_id" in self.request.query_params:
                return queryset.filter(donation=self.get_donation()).get_cached_trees()
            else:
                raise ValidationError(
                    "Either post_id or donation_id are required.", "required"
                )

        # let comment and post authors delete the comment
        elif self.action == "destroy":
            return queryset.filter(
                Q(author_user=self.request.user)
                | Q(post__author_user=self.request.user)
                | Q(donation__creator_user=self.request.user)
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "reactions":
            return CommentReactionSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        async_task(notify_comment, serializer.instance.pk)

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

    @lru_cache
    def get_donation(self):
        try:
            return Donation.objects.filter(
                Q(is_hidden=False)
                | Q(creator_user_id=self.request.user.pk)
                | Q(fan_user_id=self.request.user.pk)
            ).get(id=self.request.query_params.get("donation_id"))
        except (Donation.DoesNotExist, ValueError):
            raise ValidationError("Invalid donation_id.")

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


class PostImageViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = PostImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreator]

    def get_queryset(self):
        return self.request.user.post_images.all()

    def perform_create(self, serializer):
        serializer.save(creator_user=self.request.user)


class SectionViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly]
    serializer_class = SectionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SectionFilter
    ordering_fields = ("name",)
    queryset = Section.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ["create", "destroy", "update", "partial_update"]:
            queryset = queryset.filter(creator_user=self.request.user)

        queryset = queryset.annotate(
            post_count=Count("posts", filter=Q(posts__is_published=True))
        )
        return queryset.order_by("name")
    
    def perform_create(self, serializer):
        serializer.save(creator_user=self.request.user)
