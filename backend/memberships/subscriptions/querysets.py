from django.db import models
from django.utils import timezone


class SubscriptionQuerySet(models.QuerySet):
    def active(self, creator_user, fan_user):
        return self.current_cycle().get(
            fan_user=fan_user,
            creator_user=creator_user,
            status__in=[
                self.model.Status.ACTIVE,
                self.model.Status.SCHEDULED_TO_CANCEL,
            ],
        )

    def current_cycle(self):
        now = timezone.now()
        return self.filter(cycle_start_at__lte=now, cycle_end_at__gte=now)
