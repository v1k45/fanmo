from trackstats.models import Domain, Metric


def register_metrics():
    """
    A separate function is needed because pytest is fucking retarded and shits the bed while tearing down.
    So many hours wasted.
    """
    # Membership stats
    Domain.objects.MEMBERSHIPS = Domain.objects.register(
        ref="memberships", name="Memberships"
    )
    Metric.objects.NEW_MEMBER_COUNT, _ = Metric.objects.update_or_create(
        domain=Domain.objects.MEMBERSHIPS,
        ref="new_member_count",
        name="Number of new members",
    )

    # Payment stats
    Domain.objects.PAYMENTS = Domain.objects.register(ref="payments", name="Payments")
    Metric.objects.TOTAL_DONATION_AMOUNT, _ = Metric.objects.update_or_create(
        domain=Domain.objects.PAYMENTS,
        ref="total_donation_amount",
        name="Total donation amount",
    )
    Metric.objects.TOTAL_MEMBERSHIP_AMOUNT, _ = Metric.objects.update_or_create(
        domain=Domain.objects.PAYMENTS,
        ref="total_membership_amount",
        name="Total membership amount",
    )
    Metric.objects.TOTAL_PAYMENT_AMOUNT, _ = Metric.objects.update_or_create(
        domain=Domain.objects.PAYMENTS,
        ref="total_payment_amount",
        name="Total payment amount",
    )
    Metric.objects.TOTAL_PAYOUT_AMOUNT, _ = Metric.objects.update_or_create(
        domain=Domain.objects.PAYMENTS,
        ref="total_payout_amount",
        name="Total payout amount",
    )
