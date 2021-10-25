from rest_framework import viewsets

from memberships.posts.api.serializers import PostSerializer
from memberships.posts.models import Post


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

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
        return super().get_queryset()
