import time
from django.db import models
from trackstats.models import (
    ByDateMixin,
    ByObjectMixin,
    AbstractStatistic,
    StatisticByDateAndObjectQuerySet,
)
from memberships.utils.models import BaseModel


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
        return int(time.mktime(self.date.timetuple()) * 1000)
