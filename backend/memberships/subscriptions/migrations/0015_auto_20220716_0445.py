# Generated by Django 3.2.8 on 2022-07-15 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0014_auto_20220710_0743"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalsubscription",
            name="scheduled_to_cancel",
        ),
        migrations.RemoveField(
            model_name="historicalsubscription",
            name="scheduled_to_change",
        ),
        migrations.RemoveField(
            model_name="subscription",
            name="scheduled_to_cancel",
        ),
        migrations.RemoveField(
            model_name="subscription",
            name="scheduled_to_change",
        ),
    ]
