from django.db import models
from django.utils import timezone


class SubscriptionQuerySet(models.QuerySet):
    def active(self, seller, buyer):
        return self.current_cycle().get(
            buyer_user=buyer,
            seller_user=seller,
            status__in=[
                self.model.Status.ACTIVE,
                self.model.Status.SCHEDULED_TO_CANCEL,
            ],
        )

    def current_cycle(self):
        now = timezone.now()
        return self.filter(cycle_start_at__lte=now, cycle_end_at__gte=now)
