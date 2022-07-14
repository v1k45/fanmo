from rest_framework import serializers


class SeriesSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.DecimalField(max_digits=15, decimal_places=2)


class StatOverviewSerializer(serializers.Serializer):
    current = serializers.DecimalField(max_digits=15, decimal_places=2)
    last = serializers.DecimalField(max_digits=15, decimal_places=2)
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
    new_member_count = StatOverviewSerializer()
    total_payment_amount = StatOverviewSerializer()
    total_donation_amount = StatOverviewSerializer()
    total_membership_amount = StatOverviewSerializer()
    total_payout_amount = StatOverviewSerializer()
    active_member_count = serializers.IntegerField()
    donation_count = serializers.IntegerField()
    meta = AnalyticsMetaSerializer()
