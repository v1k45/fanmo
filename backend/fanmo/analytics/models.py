import time

from django.db import models
from trackstats.models import (
    AbstractStatistic,
    ByDateMixin,
    ByObjectMixin,
    StatisticByDateAndObjectQuerySet,
)

from fanmo.utils.helpers import datestamp
from fanmo.utils.models import BaseModel


class StatisticByDateAndObject(
    ByDateMixin, ByObjectMixin, AbstractStatistic, BaseModel
):
    """
    Extension over trackstats' model to use decimal values instead of integer.
    """

    value = models.DecimalField(null=True, max_digits=15, decimal_places=2)
    objects = StatisticByDateAndObjectQuerySet.as_manager()

    class Meta:
        unique_together = ["date", "metric", "object_type", "object_id", "period"]
        verbose_name = "Statistic by date and object"
        verbose_name_plural = "Statistics by date and object"

    def __str__(self):
        return "{date}: {value}".format(date=self.date, value=self.value)

    def datestamp(self):
        return datestamp(self.date)


class ApplicationEvent(BaseModel):
    class EventName(models.TextChoices):
        PAYMENT_FAILED = "payment_failed"

    name = models.CharField(max_length=15, choices=EventName.choices)
    payload = models.JSONField()

    # optional, but related metadata
    donation = models.ForeignKey(
        "donations.Donation", blank=True, null=True, on_delete=models.CASCADE
    )
    subscription = models.ForeignKey(
        "memberships.Subscription", blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name
