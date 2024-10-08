# Generated by Django 3.2.14 on 2022-07-24 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("donations", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicaldonation",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical donation",
                "verbose_name_plural": "historical donations",
            },
        ),
        migrations.AlterField(
            model_name="historicaldonation",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
    ]
