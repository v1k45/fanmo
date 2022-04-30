from django_filters import rest_framework as filters
from memberships.payments.models import Payment
from memberships.donations.models import Donation
from rest_framework import serializers


class PaymentFilter(filters.FilterSet):
    creator_username = filters.CharFilter(field_name="creator_user__username")
    fan_username = filters.CharFilter(field_name="fan_user__username")
    type = filters.CharFilter(field_name="type")
    method = filters.CharFilter(field_name="method")
    membership_id = filters.NumberFilter(method="filter_membership_id")
    related_donation_id = filters.NumberFilter(method="filter_related_donation_id")

    class Meta:
        model = Payment
        fields = [
            "membership_id",
            "related_donation_id",
            "creator_username",
            "fan_username",
            "type",
        ]

    def filter_membership_id(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            type=Payment.Type.SUBSCRIPTION, subscription__membership_id=value
        )

    def filter_related_donation_id(self, queryset, name, value):
        if not value:
            return queryset

        donation = Donation.objects.filter(id=value).first()
        if not donation:
            raise serializers.ValidationError(
                {name: serializers.ErrorDetail("Invalid related_donation_id.")}
            )

        return queryset.filter(
            type=Payment.Type.DONATION,
            donation__creator_user=donation.creator_user_id,
            donation__fan_user=donation.fan_user_id,
        )
