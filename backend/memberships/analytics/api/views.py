from functools import lru_cache
from time import mktime
from dateutil.rrule import rrule, DAILY
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import ValidationError, ErrorDetail
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dateutil.relativedelta import relativedelta
from memberships.utils.helpers import datestamp
from memberships.analytics.api.serializers import AnalyticsSerializer
from memberships.utils.money import percent_change

from memberships.analytics.models import StatisticByDateAndObject
from memberships.subscriptions.models import Membership
from memberships.donations.models import Donation
from trackstats.models import Metric
from memberships.users.api.permissions import IsCreator


class AnalyticsAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCreator]
    serializer_class = AnalyticsSerializer

    def get(self, *args, **kwargs):
        current_range, last_range = self.get_filter_date_range()
        stats = {
            # individual metrics
            "new_member_count": self.get_stats(
                self.query_stats(Metric.objects.NEW_MEMBER_COUNT, *current_range),
                self.query_stats(Metric.objects.NEW_MEMBER_COUNT, *last_range),
            ),
            "total_donation_amount": self.get_stats(
                self.query_stats(Metric.objects.TOTAL_DONATION_AMOUNT, *current_range),
                self.query_stats(Metric.objects.TOTAL_DONATION_AMOUNT, *last_range),
            ),
            "total_membership_amount": self.get_stats(
                self.query_stats(
                    Metric.objects.TOTAL_MEMBERSHIP_AMOUNT, *current_range
                ),
                self.query_stats(Metric.objects.TOTAL_MEMBERSHIP_AMOUNT, *last_range),
            ),
            "total_payment_amount": self.get_stats(
                self.query_stats(Metric.objects.TOTAL_PAYMENT_AMOUNT, *current_range),
                self.query_stats(Metric.objects.TOTAL_PAYMENT_AMOUNT, *last_range),
            ),
            "total_payout_amount": self.get_stats(
                self.query_stats(Metric.objects.TOTAL_PAYOUT_AMOUNT, *current_range),
                self.query_stats(Metric.objects.TOTAL_PAYOUT_AMOUNT, *last_range),
            ),
            # lifetime metrics
            "active_member_count": Membership.objects.filter(
                is_active=True, creator_user=self.request.user
            ).count(),
            "donation_count": Donation.objects.filter(
                status=Donation.Status.SUCCESSFUL, creator_user=self.request.user
            ).count(),
            # metadata
            "meta": {
                "current_date_range": [
                    current_range[0].date(),
                    current_range[1].date(),
                ],
                "last_date_range": [last_range[0].date(), last_range[1].date()],
            },
        }
        return Response(self.get_serializer(stats).data)

    @lru_cache
    def get_filter_date_range(self):
        """
        Based on current datetime and URL parameter,
        find out current and last filter ranges for querying stats.

        Returns
        -------
        tuple : tuple, tuple
                (current_start_date, current_upto_date), (last_start_date, last_upto_date)
        """
        period = self.request.query_params.get("period", "week")
        if period not in ["week", "month", "lifetime"]:
            raise ValidationError({"period": ErrorDetail("Invalid period selected.")})

        current_upto_date = timezone.localtime()
        if period == "week":
            current_start_date = current_upto_date - relativedelta(days=7)
            # stop last date range just a day before current date range starts
            last_upto_date = current_start_date - relativedelta(days=1)
            last_start_date = last_upto_date - relativedelta(days=7)
        elif period == "month":
            current_start_date = current_upto_date - relativedelta(days=30)
            # stop last date range just a day before current date range starts
            last_upto_date = current_start_date - relativedelta(days=1)
            last_start_date = last_upto_date - relativedelta(days=30)
        else:
            current_start_date = self.request.user.date_joined
            # invalid dates which will yield no results.
            last_upto_date = current_start_date - relativedelta(days=1)
            last_start_date = last_upto_date - relativedelta(days=1)

        current_start_date = current_start_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        current_upto_date = current_upto_date.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        last_start_date = last_start_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        last_upto_date = last_upto_date.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        return (
            (current_start_date, current_upto_date),
            (last_start_date, last_upto_date),
        )

    def query_stats(self, metric, start_date, end_date):
        return StatisticByDateAndObject.objects.narrow(
            from_date=start_date,
            to_date=end_date,
            object=self.request.user,
            metric=metric,
        ).order_by("date")

    def get_stats(self, current_stats, last_stats):
        (start_at, end_at), _ = self.get_filter_date_range()
        series = {
            datestamp(datetime.date()): "0.00"
            for datetime in rrule(dtstart=start_at, until=end_at, freq=DAILY)
        }
        result = {
            "current": 0,
            "last": 0,
            "percent_change": None,
            "series": [],
        }
        for stat in current_stats:
            result["current"] += stat.value
            series[stat.datestamp()] = stat.value

        for stat in last_stats:
            result["last"] += stat.value

        result["series"] = [{"x": key, "y": value} for key, value in series.items()]
        result["percent_change"] = percent_change(result["current"], result["last"])
        return result
