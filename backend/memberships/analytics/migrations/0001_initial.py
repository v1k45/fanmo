# Generated by Django 3.2.8 on 2022-07-21 00:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("trackstats", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatisticByDateAndObject",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "period",
                    models.IntegerField(
                        choices=[
                            (86400, "Day"),
                            (604800, "Week"),
                            (2419200, "28 days"),
                            (2592000, "Month"),
                            (0, "Lifetime"),
                        ]
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                ("date", models.DateField(db_index=True)),
                (
                    "value",
                    models.DecimalField(decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "metric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="statistic_by_date_and_objects",
                        to="trackstats.metric",
                    ),
                ),
                (
                    "object_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="statistic_by_date_and_objects",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Statistic by date and object",
                "verbose_name_plural": "Statistics by date and object",
                "db_table": "statistic_by_date_and_objects",
                "ordering": ("-created_at",),
                "default_related_name": "statistic_by_date_and_objects",
                "unique_together": {
                    ("date", "metric", "object_type", "object_id", "period")
                },
            },
        ),
    ]
