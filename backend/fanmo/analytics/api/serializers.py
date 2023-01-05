from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import serializers

from fanmo.analytics.models import ApplicationEvent
from fanmo.donations.models import Donation
from fanmo.memberships.models import Subscription


class SeriesSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.DecimalField(max_digits=15, decimal_places=2)


class StatOverviewSerializer(serializers.Serializer):
    current = serializers.DecimalField(max_digits=15, decimal_places=2)
    last = serializers.DecimalField(max_digits=15, decimal_places=2)
    percent_change = serializers.DecimalField(max_digits=15, decimal_places=2)
    series = SeriesSerializer(many=True)


class IntStatOverviewSerializer(serializers.Serializer):
    current = serializers.IntegerField()
    last = serializers.IntegerField()
    percent_change = serializers.DecimalField(max_digits=15, decimal_places=2)
    series = SeriesSerializer(many=True)


class AnalyticsMetaSerializer(serializers.Serializer):
    current_date_range = serializers.ListField(
        child=serializers.DateField(read_only=True),
        min_length=2,
        max_length=2,
    )
    last_date_range = serializers.ListField(
        child=serializers.DateField(read_only=True),
        min_length=2,
        max_length=2,
    )


class AnalyticsSerializer(serializers.Serializer):
    new_member_count = IntStatOverviewSerializer()
    total_payment_amount = StatOverviewSerializer()
    total_donation_amount = StatOverviewSerializer()
    total_membership_amount = StatOverviewSerializer()
    total_payout_amount = StatOverviewSerializer()
    active_member_count = serializers.IntegerField()
    donation_count = serializers.IntegerField()
    meta = AnalyticsMetaSerializer()


class ApplicationEventSerializer(serializers.ModelSerializer):
    donation_id = serializers.PrimaryKeyRelatedField(
        source="donation",
        required=False,
        allow_null=True,
        queryset=Donation.objects.all(),
    )
    subscription_id = serializers.PrimaryKeyRelatedField(
        source="subscription",
        required=False,
        allow_null=True,
        queryset=Subscription.objects.all(),
    )

    class Meta:
        model = ApplicationEvent
        fields = ["id", "name", "payload", "donation_id", "subscription_id"]

    def validate(self, attrs):
        if attrs["donation"] is None and attrs["subscription"] is None:
            raise serializers.ValidationError(
                "subcription_id or donation_id is required."
            )
        return attrs

    def validate_donation_id(self, donation):
        if not donation:
            return None

        similar_events = ApplicationEvent.objects.filter(donation=donation)
        if (
            donation.created_at < (timezone.now() - relativedelta(minutes=15))
            or similar_events.count() > 15
        ):
            raise serializers.ValidationError(
                "This resource has exceeded event ingestion threshold."
            )
        return donation

    def validate_subscription_id(self, subscription):
        if not subscription:
            return None

        similar_events = ApplicationEvent.objects.filter(subscription=subscription)
        if (
            subscription.created_at < (timezone.now() - relativedelta(minutes=15))
            or similar_events.count() > 15
        ):
            raise serializers.ValidationError(
                "This resource has exceeded event ingestion threshold."
            )
        return subscription
