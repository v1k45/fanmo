from trackstats.models import Metric, Period

from fanmo.core.tasks import async_task
from fanmo.payments.models import Payment, Payout
from fanmo.subscriptions.models import Subscription

from .trackers import MembershipCountTracker, PaymentAmountTracker, PayoutAmountTracker


def refresh_stats(creator_user_id):
    refresh_total_payment_amount(creator_user_id)
    refresh_total_donation_amount(creator_user_id)
    refresh_total_membership_amount(creator_user_id)
    refresh_total_payout_amount(creator_user_id)
    refresh_new_membership_count(creator_user_id)


def refresh_all_stats():
    from fanmo.users.models import User

    for user in User.objects.filter(is_creator=True):
        async_task(refresh_stats, user.id)


def refresh_total_payment_amount(creator_user_id):
    PaymentAmountTracker(
        period=Period.DAY,
        metric=Metric.objects.TOTAL_PAYMENT_AMOUNT,
    ).track(
        Payment.objects.filter(
            creator_user_id=creator_user_id,
            status=Payment.Status.CAPTURED,
        )
    )


def refresh_total_donation_amount(creator_user_id):
    PaymentAmountTracker(
        period=Period.DAY,
        metric=Metric.objects.TOTAL_DONATION_AMOUNT,
    ).track(
        Payment.objects.filter(
            creator_user_id=creator_user_id,
            status=Payment.Status.CAPTURED,
            type=Payment.Type.DONATION,
        )
    )


def refresh_total_membership_amount(creator_user_id):
    PaymentAmountTracker(
        period=Period.DAY,
        metric=Metric.objects.TOTAL_MEMBERSHIP_AMOUNT,
    ).track(
        Payment.objects.filter(
            creator_user_id=creator_user_id,
            status=Payment.Status.CAPTURED,
            type=Payment.Type.SUBSCRIPTION,
        )
    )


def refresh_total_payout_amount(creator_user_id):
    PayoutAmountTracker(
        period=Period.DAY,
        metric=Metric.objects.TOTAL_PAYOUT_AMOUNT,
    ).track(
        Payout.objects.filter(
            payment__creator_user_id=creator_user_id,
        )
    )


def refresh_new_membership_count(creator_user_id):
    MembershipCountTracker(
        period=Period.DAY,
        metric=Metric.objects.NEW_MEMBER_COUNT,
    ).track(
        Subscription.objects.filter(
            creator_user_id=creator_user_id,
        )
    )
