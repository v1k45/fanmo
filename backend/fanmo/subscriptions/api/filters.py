from django_filters import rest_framework as filters

from fanmo.subscriptions.models import Membership


class MembershipFilter(filters.FilterSet):
    creator_username = filters.CharFilter(field_name="creator_user__username")
    fan_username = filters.CharFilter(field_name="fan_user__username")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Membership
        fields = ["creator_username", "fan_username", "tier_id", "is_active"]
