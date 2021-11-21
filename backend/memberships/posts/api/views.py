from rest_framework import viewsets, mixins, permissions

from memberships.posts.api.serializers import PostCreateSerializer, PostSerializer
from memberships.posts.models import Post


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
        queryset = super().get_queryset()
        queryset = queryset.select_related("minimum_tier")
        username = self.request.query_params.get("username")
        if username:
            return queryset.filter(author_user__username=username)

        if self.request.user.is_authenticated:
            return queryset.filter(author_user__followings=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.is_published = False
        instance.save()
