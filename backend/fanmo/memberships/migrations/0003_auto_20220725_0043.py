# Generated by Django 3.2.14 on 2022-07-24 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("memberships", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalmembership",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical membership",
                "verbose_name_plural": "historical memberships",
            },
        ),
        migrations.AlterModelOptions(
            name="historicalsubscription",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical subscription",
                "verbose_name_plural": "historical subscriptions",
            },
        ),
        migrations.AlterModelOptions(
            name="historicaltier",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical tier",
                "verbose_name_plural": "historical tiers",
            },
        ),
        migrations.AlterField(
            model_name="historicalmembership",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalsubscription",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicaltier",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
    ]
