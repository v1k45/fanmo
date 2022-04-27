from django_filters import rest_framework as filters
from memberships.donations.models import Donation


class DonationFilter(filters.FilterSet):
    creator_username = filters.CharFilter(field_name="creator_user__username")
    fan_username = filters.CharFilter(field_name="fan_user__username")

    class Meta:
        model = Donation
        fields = ["creator_username", "fan_username"]
