from django_filters import rest_framework as filters

from fanmo.users.models import User


class UserFilter(filters.FilterSet):
    is_following = filters.BooleanFilter(method="filter_is_following")
    is_creator = filters.BooleanFilter(field_name="is_creator")

    class Meta:
        model = User
        fields = ["is_creator", "is_following", "is_featured"]

    def filter_is_following(self, queryset, name, value):
        if not value:
            return queryset
        if self.request.user.is_authenticated:
            return queryset.filter(followers=self.request.user.pk)
        return queryset.none()
