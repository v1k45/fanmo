from django.db import models
from django.db.models.functions.datetime import TruncDate
from datetime import date, timedelta, datetime, time
from django.utils import timezone

from trackstats.trackers import ObjectsByDateAndObjectTracker
from trackstats.models import Period
from memberships.users.models import User
from memberships.analytics.models import StatisticByDateAndObject


class ObjectTracker(ObjectsByDateAndObjectTracker):
    """
    Helper class to scrape stats with day and lifetime period.

    Day-wise period represents the total daily stat for the given metric.
    For example, we might want to store how much total payment a creator processed on a certian day.

    Lifetime period represents the total stat UPTO the day when the stat was recorded.
    For example, we might want to store how much lifetime payment a creator processed till a certain date.

    Ideally lifetime stat could be calculated using a simple WHERE on the actual model
    but in some cases we need to store the data separately.
    Memberships, for example, are calculated using a moving window where it is possible that a membership
    is active for a month, but not in past or future.

    Now, how the fuck do I take decrease in membership into account?
    """

    statistic_model = StatisticByDateAndObject

    def track(self, qs):
        """
        Track stats from a queryset
        """
        to_date = date.today()
        start_date = self.get_start_date(qs)
        if not start_date:
            return
        if self.period == Period.LIFETIME:
            self.track_lifetime(qs, start_date, to_date)
        elif self.period == Period.DAY:
            self.track_day(qs, start_date)
        else:
            raise NotImplementedError

    def track_lifetime(self, qs, start_date, to_date):
        """
        Track lifetime stats for a given queryset
        """
        # Intentionally recompute last stat, as we may have computed
        # that the last time when the day was not over yet.
        upto_date = start_date
        while upto_date <= to_date:
            self.track_lifetime_upto(qs, upto_date)
            upto_date += timedelta(days=1)

    def track_lifetime_upto(self, qs, upto_date):
        upto_dt = timezone.make_aware(datetime.combine(upto_date, time.max))
        for value in self.filter_lifetime_queryset(qs, upto_dt):
            self.statistic_model.objects.record(
                metric=self.metric,
                value=value["ts_n"],
                date=upto_date,
                period=self.period,
                **self.get_record_kwargs(value)
            )

    def filter_lifetime_queryset(self, qs, upto_date):
        return (
            qs.filter(**{self.date_field + "__lte": upto_date})
            .values(self.object_field)
            .annotate(ts_n=self.aggr_op)
            .order_by()
        )

    def track_day(self, qs, start_date):
        start_dt = timezone.make_aware(
            datetime.combine(start_date, time()) - timedelta(days=1)
        )
        for value in self.filter_day_queryset(qs, start_dt):
            self.statistic_model.objects.record(
                metric=self.metric,
                value=value["ts_n"],
                date=value["ts_date"],
                period=self.period,
                **self.get_record_kwargs(value)
            )

    def filter_day_queryset(self, qs, start_dt):
        return (
            qs.filter(**{self.date_field + "__gte": start_dt})
            .annotate(ts_date=TruncDate(self.date_field))
            .values("ts_date", *self.get_track_values())
            .annotate(ts_n=self.aggr_op)
            .order_by()
        )


class PaymentAmountTracker(ObjectTracker):
    aggr_op = models.Sum("amount")
    object_model = User
    object_field = "creator_user"
    date_field = "created_at"


class PayoutAmountTracker(ObjectTracker):
    aggr_op = models.Sum("amount")
    object_model = User
    object_field = "payment__creator_user"
    date_field = "created_at"


class MembershipCountTracker(ObjectTracker):
    """
    Extension of the default tracker to support date range based
    lookup to facilitate counting active membership historically.
    """

    date_field = "cycle_start_at"
    object_model = User
    object_field = "creator_user"
    aggr_op = models.Count("membership_id", distinct=True)

    def filter_day_queryset(self, qs, start_dt):
        return (
            qs.active_at(start_dt)
            .annotate(ts_date=TruncDate(self.date_field))
            .values("ts_date", *self.get_track_values())
            .order_by()
            .annotate(ts_n=self.aggr_op)
        )

    def filter_lifetime_queryset(self, qs, upto_date):
        return (
            qs.active_before(upto_date)
            .values(self.object_field)
            .annotate(ts_n=self.aggr_op)
            .order_by()
        )
