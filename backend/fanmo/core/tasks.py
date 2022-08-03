from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import async_task as q_async_task
from django_q.tasks import schedule


def register_scheduled_tasks():
    tasks = [
        {
            "name": "refresh_all_memberships",
            "defaults": {
                "func": "fanmo.memberships.tasks.refresh_all_memberships",
                "schedule_type": Schedule.DAILY,
            },
        },
        {
            "name": "refresh_all_stats",
            "defaults": {
                "func": "fanmo.analytics.tasks.refresh_all_stats",
                "schedule_type": Schedule.DAILY,
            },
        },
    ]
    for task in tasks:
        Schedule.objects.update_or_create(**task)


def async_task(func, *args, **kwargs):
    if settings.Q_CLUSTER.get("sync"):
        # task scheduling does not work while running tests
        q_async_task(func, *args, **kwargs)
    else:
        kwargs["next_run"] = timezone.now() + relativedelta(seconds=3)
        schedule(f"{func.__module__}.{func.__name__}", *args, **kwargs)
