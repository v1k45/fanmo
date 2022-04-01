# Generated by Django 3.2.8 on 2022-03-31 23:40

from django.conf import settings
from django.db import migrations


def set_fan_users(apps, _):
    Donation = apps.get_model("donations.Donation")
    User = apps.get_model("users.User")
    first_user = User.objects.first()
    Donation.objects.filter(fan_user__isnull=True).update(fan_user=first_user)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("donations", "0005_historicaldonation"),
    ]

    operations = [
        migrations.RunPython(set_fan_users, migrations.RunPython.noop),
    ]
