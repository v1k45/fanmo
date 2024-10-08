# Generated by Django 3.2.14 on 2022-10-21 07:48

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("memberships", "0004_auto_20221002_1647"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicaltier",
            name="benefits",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255), default=list, size=10
            ),
        ),
        migrations.AlterField(
            model_name="tier",
            name="benefits",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255), default=list, size=10
            ),
        ),
    ]
