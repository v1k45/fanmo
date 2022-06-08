from django_q.models import Schedule


def register_scheduled_tasks():
    tasks = [
        {
            "name": "refresh_all_memberships",
            "defaults": {
                "func": "memberships.subscriptions.tasks.refresh_all_memberships",
                "schedule_type": Schedule.DAILY,
            },
        },
        {
            "name": "refresh_all_stats",
            "defaults": {
                "func": "memberships.analytics.tasks.refresh_all_stats",
                "schedule_type": Schedule.DAILY,
            },
        },
    ]
    for task in tasks:
        Schedule.objects.update_or_create(**task)
