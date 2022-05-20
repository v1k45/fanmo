from rest_framework.generics import GenericAPIView

from memberships.analytics.models import StatisticByDateAndObject, Metric


class AnalyticsAPIView(GenericAPIView):
    def get(self, *args, **kwargs):
        """"
        get filter param
            - period=week|month|lifetime

        response style:
            - stat_name: {value: 1, last_value: 1, percent_change: 0, series: []}
        """
        stat = StatisticByDateAndObject.objects.narrow(
            from_date=None,
            to_date=None,
            object=self.request.user,
            metrics=[
                Metric.objects.ACTIVE_MEMBERS_COUNT,
                Metric.objects.TOTAL_DONATION_AMOUNT,
                Metric.objects.TOTAL_MEMBERSHIP_AMOUNT,
                Metric.objects.TOTAL_PAYMENT_AMOUNT,
                Metric.objects.TOTAL_PAYOUT_AMOUNT,
            ]
        )

    def get_filter_date_range(self, upto_date):
        start_date = self.request.user.date_joined
        period = self.request.query_params.get("period", "week")
        if period == "lifetime":
            start_date = ''
        return upto_date, upto_date
