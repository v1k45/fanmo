from trackstats.models import (
    Domain,
    Metric,
)


# Membership stats
Domain.objects.MEMBERSHIPS = Domain.objects.register(
    ref="memberships", name="Memberships"
)
Metric.objects.ACTIVE_MEMBERS_COUNT = Metric.objects.register(
    domain=Domain.objects.MEMBERSHIPS,
    ref="active_members_count",
    name="Number of active members",
)

# Payment stats
Domain.objects.PAYMENTS = Domain.objects.register(ref="payments", name="Payments")
Metric.objects.TOTAL_DONATION_AMOUNT = Metric.objects.register(
    domain=Domain.objects.PAYMENTS,
    ref="total_donation_amount",
    name="Total donation amount",
)
Metric.objects.TOTAL_MEMBERSHIP_AMOUNT = Metric.objects.register(
    domain=Domain.objects.PAYMENTS,
    ref="total_membership_amount",
    name="Total membership amount",
)
Metric.objects.TOTAL_PAYMENT_AMOUNT = Metric.objects.register(
    domain=Domain.objects.PAYMENTS,
    ref="total_payment_amount",
    name="Total payment amount",
)
Metric.objects.TOTAL_PAYOUT_AMOUNT = Metric.objects.register(
    domain=Domain.objects.PAYMENTS,
    ref="total_payout_amount",
    name="Total payout amount",
)
