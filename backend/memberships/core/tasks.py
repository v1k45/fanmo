from django_q.models import Schedule


def register_scheduled_tasks():
    tasks = [
        {
            "func": "memberships.subscriptions.tasks.refresh_all_memberships",
            "schedule_type": Schedule.HOURLY,
        },
        {
            "func": "memberships.subscriptions.tasks.refresh_all_stats",
            "schedule_type": Schedule.HOURLY,
        },
    ]
    for task in tasks:
        Schedule.objects.get_or_create(**task)
