from datetime import datetime
from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from moneyed import INR, Money
from trackstats.models import Metric, Period

from fanmo.analytics.models import StatisticByDateAndObject
from fanmo.analytics.tasks import refresh_stats
from fanmo.memberships.models import Membership, Plan
from fanmo.memberships.tasks import refresh_creator_memberships, refresh_membership
from fanmo.memberships.tests.factories import (
    MembershipFactory,
    PlanFactory,
    SubscriptionFactory,
    TierFactory,
)
from fanmo.payments.models import Payment, Payout
from fanmo.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestRefreshStats:
    def test_refresh_payment_stats(self, creator_user, user, time_machine):
        now = timezone.now()

        assert StatisticByDateAndObject.objects.count() == 0

        def create_payment(
            amount="100", type=Payment.Type.DONATION, status=Payment.Status.CAPTURED
        ):
            return Payment.objects.create(
                amount=Money(Decimal(amount), INR),
                status=status,
                type=type,
                external_id="x123",
                creator_user=creator_user,
                fan_user=user,
            )

        time_machine.move_to(datetime(2021, 1, 1))
        create_payment(amount="100", type=Payment.Type.DONATION)
        refresh_stats(creator_user.id)
        create_payment(amount="100", type=Payment.Type.DONATION)
        create_payment(amount="500", type=Payment.Type.SUBSCRIPTION)
        refresh_stats(creator_user.id)
        create_payment(amount="500", type=Payment.Type.SUBSCRIPTION)

        # refunded payments should be excluded from calculation
        create_payment(
            amount="5", type=Payment.Type.SUBSCRIPTION, status=Payment.Status.REFUNDED
        )
        refresh_stats(creator_user.id)

        time_machine.move_to(datetime(2021, 2, 1))
        create_payment(amount="1000", type=Payment.Type.DONATION)
        create_payment(amount="5000", type=Payment.Type.SUBSCRIPTION)

        refresh_stats(creator_user.id)
        create_payment(amount="1000", type=Payment.Type.DONATION)
        create_payment(amount="5000", type=Payment.Type.SUBSCRIPTION)

        time_machine.move_to(now)
        refresh_stats(creator_user.id)

        stats = StatisticByDateAndObject.objects.narrow(
            metric=Metric.objects.TOTAL_PAYMENT_AMOUNT,
            object=creator_user,
            period=Period.DAY,
        )
        assert len(stats) == 2

        assert stats[0].date.isoformat() == "2021-02-01"
        assert stats[0].value == Decimal("12000")

        assert stats[1].date.isoformat() == "2021-01-01"
        assert stats[1].value == Decimal("1200")

        stats = StatisticByDateAndObject.objects.narrow(
            metric=Metric.objects.TOTAL_DONATION_AMOUNT,
            object=creator_user,
            period=Period.DAY,
        )
        assert len(stats) == 2

        assert stats[0].date.isoformat() == "2021-02-01"
        assert stats[0].value == Decimal("2000")

        assert stats[1].date.isoformat() == "2021-01-01"
        assert stats[1].value == Decimal("200")

        stats = StatisticByDateAndObject.objects.narrow(
            metric=Metric.objects.TOTAL_MEMBERSHIP_AMOUNT,
            object=creator_user,
            period=Period.DAY,
        )
        assert len(stats) == 2

        assert stats[0].date.isoformat() == "2021-02-01"
        assert stats[0].value == Decimal("10000")

        assert stats[1].date.isoformat() == "2021-01-01"
        assert stats[1].value == Decimal("1000")

    def test_refresh_payout_stats(self, creator_user, user, time_machine):
        now = timezone.now()

        assert StatisticByDateAndObject.objects.count() == 0

        def create_payout(amount="100"):
            return Payout.objects.create(
                amount=Money(Decimal(amount), INR),
                status=Payout.Status.PROCESSED,
                external_id="x123",
                payment=Payment.objects.create(
                    amount=Money(Decimal(amount), INR),
                    creator_user=creator_user,
                    fan_user=user,
                    type=Payment.Type.DONATION,
                ),
                bank_account=creator_user.bank_accounts.get(),
            )

        time_machine.move_to(datetime(2021, 1, 1))
        create_payout(amount="100")
        refresh_stats(creator_user.id)
        create_payout(amount="50")
        refresh_stats(creator_user.id)

        time_machine.move_to(datetime(2021, 2, 1))
        create_payout(amount="1000")
        create_payout(amount="500")
        refresh_stats(creator_user.id)

        time_machine.move_to(now)
        refresh_stats(creator_user.id)

        stats = StatisticByDateAndObject.objects.narrow(
            metric=Metric.objects.TOTAL_PAYOUT_AMOUNT,
            object=creator_user,
            period=Period.DAY,
        )
        assert len(stats) == 2

        assert stats[0].date.isoformat() == "2021-02-01"
        assert stats[0].value == Decimal("1500")

        assert stats[1].date.isoformat() == "2021-01-01"
        assert stats[1].value == Decimal("150")

    def test_refresh_membership_stats(self, creator_user, mocker, time_machine):
        rzp_plan_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.plan.create",
            return_value={"id": "plan_456"},
        )
        rzp_sub_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.patch_url",
            return_value={"id": "sub_456"},
        )

        now = timezone.now()
        assert StatisticByDateAndObject.objects.count() == 0

        def create_membership(fan_user, cycle_start_at):
            membership = MembershipFactory(
                creator_user=creator_user,
                fan_user=fan_user,
            )
            plan = PlanFactory(tier=creator_user.tiers.get())
            subscription = SubscriptionFactory(
                plan=plan,
                membership=membership,
                creator_user=creator_user,
                fan_user=fan_user,
                cycle_start_at=cycle_start_at,
                cycle_end_at=cycle_start_at + relativedelta(months=1),
            )
            membership.scheduled_subscription = subscription
            membership.save()
            return membership

        def activate_membership(membership):
            subscription = membership.scheduled_subscription
            subscription.authenticate()
            subscription.activate()
            subscription.save()

        time_machine.move_to(datetime(2020, 1, 1))
        user_ashok = UserFactory(username="ashok")

        # create an unauthenticated subscription - it should not show up in stats.
        ashok_membership: Membership = create_membership(user_ashok, timezone.now())
        refresh_stats(creator_user.id)
        assert StatisticByDateAndObject.objects.count() == 0

        # stats show up after membership activation
        activate_membership(ashok_membership)
        refresh_stats(creator_user.id)

        new_stats = StatisticByDateAndObject.objects.narrow(
            metric=Metric.objects.NEW_MEMBER_COUNT,
            object=creator_user,
            period=Period.DAY,
        )
        assert len(new_stats) == 1

        assert new_stats[0].date.isoformat() == "2020-01-01"
        assert new_stats[0].value == Decimal("1")

        # a new member subscribes on the same day
        time_machine.move_to(timezone.now() + relativedelta(hours=3))
        user_aarti = UserFactory(username="aarti")
        aarti_membership: Membership = create_membership(user_aarti, timezone.now())
        activate_membership(aarti_membership)
        refresh_creator_memberships(creator_user.id)
        refresh_stats(creator_user.id)

        # a new member subscribes after couple of days
        time_machine.move_to(datetime(2020, 1, 15))
        user_anuj = UserFactory(username="anuj")
        anuj_membership: Membership = create_membership(user_anuj, timezone.now())
        activate_membership(anuj_membership)
        refresh_stats(creator_user.id)

        # simulate that subscription fails payment in next cycle
        ashok_membership.refresh_from_db()
        time_machine.move_to(ashok_membership.active_subscription.cycle_end_at)

        refresh_creator_memberships(creator_user.id)
        refresh_stats(creator_user.id)

        # sumulate membership renew for aarti
        time_machine.move_to(timezone.now() + relativedelta(days=3))
        aarti_membership.refresh_from_db()
        aarti_subscription = aarti_membership.active_subscription
        aarti_subscription.renew(
            aarti_subscription.cycle_end_at + relativedelta(months=1)
        )
        aarti_subscription.save()

        refresh_creator_memberships(creator_user.id)
        refresh_stats(creator_user.id)

        # schedule anuj membership to change
        time_machine.move_to(datetime(2020, 2, 13))
        new_tier = TierFactory(
            creator_user=creator_user, amount=Money(Decimal("150"), INR)
        )
        anuj_membership.update(new_tier, Plan.Period.MONTHLY)

        time_machine.move_to(anuj_membership.active_subscription.cycle_end_at)
        refresh_creator_memberships(creator_user.id)
        refresh_stats(creator_user.id)

        new_stats = StatisticByDateAndObject.objects.narrow(
            metric=Metric.objects.NEW_MEMBER_COUNT,
            object=creator_user,
            period=Period.DAY,
        )
        assert len(new_stats) == 3

        assert new_stats[0].date.isoformat() == "2020-02-15"
        assert new_stats[0].value == Decimal("1")

        assert new_stats[1].date.isoformat() == "2020-01-15"
        assert new_stats[1].value == Decimal("1")

        assert new_stats[2].date.isoformat() == "2020-01-01"
        assert new_stats[2].value == Decimal("2")

        assert (
            Membership.objects.filter(is_active=True)
            .filter(fan_user__in=[user_aarti, user_anuj])
            .count()
            == 2
        )
