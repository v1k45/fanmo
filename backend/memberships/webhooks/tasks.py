from decimal import Decimal

from django.db.transaction import atomic
from django_fsm import can_proceed
from moneyed import Money, get_currency

from memberships.donations.models import Donation
from memberships.payments.models import Payment, Payout
from memberships.subscriptions.models import Subscription
from memberships.subscriptions.tasks import refresh_membership
from memberships.webhooks.models import WebhookMessage


@atomic
def process_razorpay_webhook(webhook_message_id):
    webhook_message = WebhookMessage.objects.get(pk=webhook_message_id)

    handlers = {
        "subscription.charged": subscription_charged,
        "subscription.cancelled": subscription_cancelled,
        "subscription.pending": subscription_pending,
        "subscription.halted": subscription_halted,
        "order.paid": order_paid,
        "transfer.processed": transfer_processed,
    }
    event_name = webhook_message.payload["event"]
    if event_name in handlers:
        handlers[event_name](webhook_message.payload)

    webhook_message.is_processed = True
    webhook_message.save()


def subscription_charged(payload):
    """
    Update subscription expiration date, record payment, issue a payout.
    """
    # nowait and try later?
    # it is possible that multiple exists.
    subscription_payload = payload["payload"]["subscription"]["entity"]
    subscription = Subscription.objects.select_for_update().get(
        external_id=subscription_payload["id"],
        plan__external_id=subscription_payload["plan_id"],
    )

    # hard fail instead?
    if can_proceed(subscription.activate):
        subscription.activate()
        subscription.payment_method = subscription_payload["payment_method"]
        subscription.save()

    payment_payload = payload["payload"]["payment"]["entity"]
    payment, _ = Payment.objects.update_or_create(
        type=Payment.Type.SUBSCRIPTION,
        subscription=subscription,
        amount=get_money_from_subunit(
            payment_payload["amount"], payment_payload["currency"]
        ),
        external_id=payment_payload["id"],
        creator_user=subscription.creator_user,
        fan_user=subscription.fan_user,
        defaults={
            "status": Payment.Status.AUTHORIZED,
            "method": payment_payload["method"],
        },
    )

    payment.status = Payment.Status.CAPTURED
    payment.save()

    # send payout
    Payout.for_payment(payment)


def subscription_cancelled(payload):
    """
    Subscription is cancelled. This could happen both, internally and externally.
    """
    subscription_payload = payload["payload"]["subscription"]["entity"]
    subscription = Subscription.objects.select_for_update().get(
        external_id=subscription_payload["id"],
        plan__external_id=subscription_payload["plan_id"],
    )
    subscription.status = Subscription.Status.CANCELLED
    subscription.save()


def subscription_halted(payload):
    """
    There were repeated payment failures while renewing.
    Manual intervention is needed from the user.
    """
    subscription_payload = payload["payload"]["subscription"]["entity"]
    subscription = Subscription.objects.select_for_update().get(
        external_id=subscription_payload["id"],
        plan__external_id=subscription_payload["plan_id"],
    )
    refresh_membership(subscription.membership_id)


def subscription_pending(payload):
    """
    There was a payment failure while renewing a subscription.
    Subscription is scheduled to retry.
    """
    subscription_payload = payload["payload"]["subscription"]["entity"]
    subscription = Subscription.objects.get(
        external_id=subscription_payload["id"],
        plan__external_id=subscription_payload["plan_id"],
    )
    refresh_membership(subscription.membership_id)


def order_paid(payload):
    """
    Update donation publish state, record payment, issue a payout.
    """
    order_id = payload["payload"]["order"]["entity"]["id"]
    if not Donation.objects.filter(external_id=order_id).exists():
        # donation with this order id does not exists.
        # this was most likely a subscription
        return

    donation = Donation.objects.select_for_update().get(external_id=order_id)

    payment_payload = payload["payload"]["payment"]["entity"]
    payment, _ = Payment.objects.update_or_create(
        type=Payment.Type.DONATION,
        donation=donation,
        amount=get_money_from_subunit(
            payment_payload["amount"], payment_payload["currency"]
        ),
        external_id=payment_payload["id"],
        creator_user=donation.creator_user,
        fan_user=donation.fan_user,
        defaults={
            "status": Payment.Status.CAPTURED,
            "method": payment_payload["method"],
        },
    )

    payment.status = Payment.Status.CAPTURED
    payment.save()

    # send payout
    Payout.for_payment(payment)


def transfer_processed(payload):
    transfer_id = payload["payload"]["transfer"]["entity"]["id"]
    Payout.objects.filter(
        external_id=transfer_id, status=Payout.Status.SCHEDULED
    ).update(status=Payout.Status.PROCESSED)


def get_money_from_subunit(amount, currency_code):
    currency = get_currency(currency_code)
    return Money(Decimal(amount) / currency.sub_unit, currency.code)
