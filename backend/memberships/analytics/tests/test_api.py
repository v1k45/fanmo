from decimal import Decimal
import pytest
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from trackstats.models import Period, Metric
from memberships.analytics.models import StatisticByDateAndObject
from memberships.utils.helpers import datestamp

pytestmark = pytest.mark.django_db


class TestAnalyticsAPI:
    @pytest.mark.parametrize(
        "metric_ref",
        [
            "total_payment_amount",
            "total_payout_amount",
            "total_donation_amount",
            "total_membership_amount",
            "new_member_count",
        ],
    )
    def test_week_metrics(self, creator_user, api_client, metric_ref):
        today = timezone.localtime().date()
        # create data for last period
        default_stat_kwargs = {
            "metric": Metric.objects.get(ref=metric_ref),
            "object": creator_user,
            "period": Period.DAY,
        }
        # this one should not be included in the response.
        StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=16),
            value=Decimal("400"),
            **default_stat_kwargs
        )
        StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=14),
            value=Decimal("10"),
            **default_stat_kwargs
        )
        StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=10),
            value=Decimal("90"),
            **default_stat_kwargs
        )

        stat1 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=7),
            value=Decimal("50"),
            **default_stat_kwargs
        )
        stat2 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=1),
            value=Decimal("100"),
            **default_stat_kwargs
        )

        api_client.force_authenticate(creator_user)
        response = api_client.get("/api/stats/")
        assert response.json()[metric_ref] == {
            "current": "150.00",
            "last": "100.00",
            "percent_change": "50.00",
            "series": [
                {"x": stat1.datestamp(), "y": "50.00"},
                {"x": datestamp(stat1.date + relativedelta(days=1)), "y": "0.00"},
                {"x": datestamp(stat1.date + relativedelta(days=2)), "y": "0.00"},
                {"x": datestamp(stat1.date + relativedelta(days=3)), "y": "0.00"},
                {"x": datestamp(stat1.date + relativedelta(days=4)), "y": "0.00"},
                {"x": datestamp(stat1.date + relativedelta(days=5)), "y": "0.00"},
                {"x": stat2.datestamp(), "y": "100.00"},
                {"x": datestamp(stat1.date + relativedelta(days=7)), "y": "0.00"},
            ],
        }

    @pytest.mark.parametrize(
        "metric_ref",
        [
            "total_payment_amount",
            "total_payout_amount",
            "total_donation_amount",
            "total_membership_amount",
            "new_member_count",
        ],
    )
    def test_month_metrics(self, creator_user, api_client, metric_ref):
        today = timezone.localtime().date()
        # create data for last period
        default_stat_kwargs = {
            "metric": Metric.objects.get(ref=metric_ref),
            "object": creator_user,
            "period": Period.DAY,
        }
        # this one should not be included in the response.
        StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=63),
            value=Decimal("400"),
            **default_stat_kwargs
        )
        StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=45),
            value=Decimal("10"),
            **default_stat_kwargs
        )
        StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=31),
            value=Decimal("90"),
            **default_stat_kwargs
        )

        stat1 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=30),
            value=Decimal("50"),
            **default_stat_kwargs
        )
        stat2 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=1),
            value=Decimal("100"),
            **default_stat_kwargs
        )

        api_client.force_authenticate(creator_user)
        response = api_client.get("/api/stats/?period=month")
        assert response.json()[metric_ref] == {
            "current": "150.00",
            "last": "100.00",
            "percent_change": "50.00",
            "series": [
                {"x": stat1.datestamp(), "y": "50.00"},
                *[
                    {
                        "x": datestamp(stat1.date + relativedelta(days=i + 1)),
                        "y": "0.00",
                    }
                    for i in range(28)
                ],
                {"x": stat2.datestamp(), "y": "100.00"},
                {"x": datestamp(stat1.date + relativedelta(days=30)), "y": "0.00"},
            ],
        }

    @pytest.mark.parametrize(
        "metric_ref",
        [
            "total_payment_amount",
            "total_payout_amount",
            "total_donation_amount",
            "total_membership_amount",
            "new_member_count",
        ],
    )
    def test_lifetime_metrics(self, creator_user, api_client, metric_ref):
        creator_user.date_joined = timezone.now() - relativedelta(days=90)
        creator_user.save()

        today = timezone.localtime().date()
        default_stat_kwargs = {
            "metric": Metric.objects.get(ref=metric_ref),
            "object": creator_user,
            "period": Period.DAY,
        }
        stat1 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=60),
            value=Decimal("400"),
            **default_stat_kwargs
        )
        stat2 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=45),
            value=Decimal("10"),
            **default_stat_kwargs
        )
        stat3 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=31),
            value=Decimal("90"),
            **default_stat_kwargs
        )

        stat4 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=30),
            value=Decimal("50"),
            **default_stat_kwargs
        )
        stat5 = StatisticByDateAndObject.objects.create(
            date=today - relativedelta(days=1),
            value=Decimal("100"),
            **default_stat_kwargs
        )

        api_client.force_authenticate(creator_user)
        response = api_client.get("/api/stats/?period=lifetime")
        assert response.json()[metric_ref] == {
            "current": "650.00",
            "last": "0.00",
            "percent_change": None,
            "series": [
                *[
                    {
                        "x": datestamp(stat1.date - relativedelta(days=i + 1)),
                        "y": "0.00",
                    }
                    for i in range(30)
                ][::-1],
                {"x": stat1.datestamp(), "y": "400.00"},
                *[
                    {
                        "x": datestamp(stat1.date + relativedelta(days=i + 1)),
                        "y": "0.00",
                    }
                    for i in range(14)
                ],
                {"x": stat2.datestamp(), "y": "10.00"},
                *[
                    {
                        "x": datestamp(stat2.date + relativedelta(days=i + 1)),
                        "y": "0.00",
                    }
                    for i in range(13)
                ],
                {"x": stat3.datestamp(), "y": "90.00"},
                {"x": stat4.datestamp(), "y": "50.00"},
                *[
                    {
                        "x": datestamp(stat4.date + relativedelta(days=i + 1)),
                        "y": "0.00",
                    }
                    for i in range(28)
                ],
                {"x": stat5.datestamp(), "y": "100.00"},
                {"x": datestamp(stat5.date + relativedelta(days=1)), "y": "0.00"},
            ],
        }
