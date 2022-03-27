from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from memberships.posts.api.serializers import (
    CommentSerializer,
    PostCreateSerializer,
    PostReactionSerializer,
    PostSerializer,
)
from memberships.posts.models import Comment, Post, Reaction


class PostViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet
):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_published=True)

    def get_queryset(self):
        """
        who can see posts?

        public posts:
            - everyone

        supportor-only posts (non mvp):
            - authenticated user has donated to the author
            - gets 30 days access from last donation
            - qs.filter(author__supporters__sender=self.request.user)
            - qs.filter(author__supporters__created_at=self.request.user)

        member-only posts (non mvp - covered by min-tier):
            - authenticated user who has an active subscription with author
            - qs.filter(author__subscriptions__subscriber=self.request.user)

        min-tier posts:
            - authenticated user who is an active member of minimum tier amount
            - qs.filter(author__subscribers=self.request.user)
            - qs.filter(author__subscribers__plan__amount__gte=F('minimum_tier_level__amount'))
        """
        queryset = super().get_queryset().with_permissions(self.request.user)
        queryset = queryset.select_related("content", "author_user").prefetch_related(
            "reactions"
        )

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(author_user__username=username)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        if self.action == "reactions":
            return PostReactionSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.is_published = False
        instance.save()

    @action(
        detail=True, permission_classes=[permissions.IsAuthenticated], methods=["POST"]
    )
    def reactions(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=self.request.data, instance=self.get_object()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        base_qs = Comment.objects.filter(is_published=True)
        # require post_id when listing comments.
        if self.action == "list":
            post_id = self.request.query_params.get("post_id")
            if post_id is not None:
                return base_qs.filter(post_id=post_id)
            raise ValidationError("post_id parameter is required.")

        # let comment and post authors delete the comment
        elif self.action == "destroy":
            return base_qs.filter(
                Q(author_user=self.request.user)
                | Q(post__author_user=self.request.user)
            )

        return super().get_queryset()

    def perform_destroy(self, instance):
        # hard delete?
        instance.is_published = True
        instance.save()
