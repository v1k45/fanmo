from decimal import Decimal
from django.db.transaction import atomic
from moneyed import Money, get_currency
from memberships.payments.models import Payment, Payout
from memberships.subscriptions.models import Subscription
from memberships.webhooks.models import WebhookMessage
from memberships.donations.models import Donation


@atomic
def process_razorpay_webhook(webhook_message_id):
    webhook_message = WebhookMessage.objects.get(pk=webhook_message_id)

    handlers = {
        "subscription.charged": subscription_charged,
        "order.paid": order_paid,
    }
    event_name = webhook_message["event"]
    if event_name in handlers:
        handlers[event_name](webhook_message.payload)

    webhook_message.is_processed = True
    webhook_message.save()


def subscription_charged(payload):
    """
    Update subscription expiration date, record payment, issue a payout.
    """
    # nowait and try later?
    subscription = Subscription.objects.select_for_update().get(
        external_id=payload["payload"]["subscription"]["entity"]["id"]
    )

    payment_payload = payload["payload"]["payment"]["entity"]
    payment, _ = Payment.objects.get_or_create(
        type=Payment.Type.SUBSCRIPTION,
        subscription=subscription,
        status=Payment.Status.CAPTURED,
        amount=get_money_from_subunit(payload["amount"], payload["currency"]),
        external_id=payment_payload["id"],
        seller=subscription.seller,
        buyer=subscription.buyer,
    )

    # send payout
    Payout.for_payment(payment)


def order_paid(payload):
    """
    Update donation publish state, record payment, issue a payout.
    """
    order_id = payload["payload"]["order"]["id"]
    if not Donation.objects.filter(external_id=order_id).exists():
        # donation with this order id does not exists.
        # this was most likely a subscription
        return

    donation = Donation.objects.select_for_update().get(external_id=order_id)


def get_money_from_subunit(amount, currency_code):
    currency = get_currency(currency_code)
    return Money(Decimal(amount) / currency.sub_unit, currency.code)
