# Generated by Django 3.2.8 on 2022-03-24 01:50

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0009_remove_tier_benefits'),
    ]

    operations = [
        migrations.AddField(
            model_name='tier',
            name='benefits',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), default=list, size=8),
        ),
    ]
