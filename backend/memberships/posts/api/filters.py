from django_filters import rest_framework as filters

from memberships.posts.models import Post


class PostFilter(filters.FilterSet):
    creator_username = filters.CharFilter(field_name="author_user__username")
    is_following = filters.CharFilter(method="filter_is_following")

    class Meta:
        model = Post
        fields = ["creator_username", "is_following"]

    def filter_is_following(self, queryset, name, value):
        if value:
            return queryset.filter(author_user__followers=self.request.user.pk)
        return queryset
