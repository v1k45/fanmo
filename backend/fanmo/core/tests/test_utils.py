import pytest
from django_q.models import Schedule

pytestmark = pytest.mark.django_db


def test_scheduled_tasks():
    assert list(Schedule.objects.values("func", "schedule_type")) == [
        {
            "func": "fanmo.memberships.tasks.refresh_all_memberships",
            "schedule_type": Schedule.DAILY,
        },
        {
            "func": "fanmo.analytics.tasks.refresh_all_stats",
            "schedule_type": Schedule.DAILY,
        },
    ]
