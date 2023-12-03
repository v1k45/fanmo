from django_filters import rest_framework as filters

from fanmo.posts.models import Post, Section


class PostFilter(filters.FilterSet):
    creator_username = filters.CharFilter(field_name="author_user__username")
    is_following = filters.CharFilter(method="filter_is_following")

    class Meta:
        model = Post
        fields = ["creator_username", "is_following", "is_pinned"]

    def filter_is_following(self, queryset, name, value):
        if value:
            return queryset.filter(author_user__followers=self.request.user.pk)
        return queryset

class SectionFilter(filters.FilterSet):
    creator_username = filters.CharFilter(field_name="creator_user__username")

    class Meta:
        model = Section
        fields = ["creator_username"]
